from flask import Flask
from ..app.routes.home import home_bp
from ..app.routes.contacts import contacts_bp
from ..app.routes.interactions import interactions_bp
from ..app.routes.auth import auth_bp
import pytest
from ..app.routes.db import ContactManager
from flask_login import LoginManager
from ..app.routes.auth import User
from flask_login import login_user, logout_user


@pytest.fixture
def app():
    app = Flask(__name__, template_folder='../app/templates')
    app.register_blueprint(home_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(interactions_bp)
    app.register_blueprint(auth_bp)
    app.config['TESTING'] = True
    app.secret_key = 'test'

    # Initialize the LoginManager and associate it with the app
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Configure the login view and endpoint
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user):
        return User.get(user)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    # Create a fixture to set up an authenticated client with a logged-in user
    with client.application.test_request_context():
        # Perform the login within the request context
        user = User('ashoka')  # Replace with your user creation logic
        user.username = 'ashoka'
        login_user(user)

        yield client

        # Perform any necessary cleanup after the test
        logout_user()


@pytest.fixture
def mock_database(mocker):
   # Patch the entire mysql.connector module to mock database interactions
    mocker.patch('sqlite3.connect')

    # Mock the return value of the get_overdue_contacts method
    database_response = [
        (1, 'Kujula Kadphises', 30, '2023-01-01'),
        (2, 'Kanishka', 25, '2022-01-01'),
    ]

    user = User('ashoka')
    user.username = 'ashoka'
    user.database = "ashoka.db"

    mocker.patch.object(ContactManager,
                        'get_overdue_contacts',
                        return_value=database_response
                        )

    mocker.patch.object(User,
                        'get',
                        return_value=user
                        )


def test_not_logged_in_user_redirected_to_login_page(client):
    response = client.get('/home', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data
    assert b'<h2>Login</h2>' in response.data


def test_logged_in_user_can_access_home_page(authenticated_client, mock_database):
    response = authenticated_client.get('/home')
    assert response.status_code == 200
    assert b'<h2>Long time no speak</h2>' in response.data
    assert b'<table aria-label="home-table">' in response.data


def test_overdue_contacts_are_rendered(authenticated_client, mock_database):
    # Make assertions based on the mocked data
    response = authenticated_client.get('/home')
    assert response.status_code == 200
    assert b'Kujula Kadphises' in response.data
    assert b'Kanishka' in response.data
