from flask import Flask
from ..app.routes.auth import auth_bp
from ..app.routes.home import home_bp
from ..app.routes.contacts import contacts_bp
from ..app.routes.interactions import interactions_bp
import pytest
from ..app.routes.db import UserManager, ContactManager
import bcrypt
from flask_login import LoginManager
from ..app.routes.auth import User


@pytest.fixture
def app():
    app = Flask(__name__, template_folder='../app/templates')
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(interactions_bp)
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
def mock_user_details(mocker):
    mocker.patch('sqlite3.connect')

    # prepare mock responses
    salt = '$2b$12$VUEfecQgohf4CKkB2loTKO'
    password_hashed = bcrypt.hashpw(
        "testPassword".encode('utf-8'), salt.encode('utf-8')).decode('utf-8')

    user_details_ashoka = {
        'username': 'ashoka',
        'password': password_hashed,
        'salt': salt,
        'email': 'ashoka@maghada.com',
        'database': "ashoka.db"
    }

    user_details_bimbisara = {
        'username': 'bimbisara',
        'password': password_hashed,
        'salt': salt,
        'email': 'bimbisara@maghada.com',
        'database': "bimbisara.db"
    }

    # Define the side_effect function
    def side_effect(username):
        if username == "ashoka":
            return user_details_ashoka
        elif username == "bimbisara":
            return user_details_bimbisara
        else:
            return None

    # Patch the get_user method with the updated side_effect
    mocker.patch.object(UserManager, 'get_user', side_effect=side_effect)


@pytest.fixture
def mock_overdue_contacts(mocker):
    mocker.patch('sqlite3.connect')

    # Mock the return value of the get_overdue_contacts method
    database_response = [
        (1, 'Mahendra', 30, '2023-01-01'),
        (2, 'Pushyamitra', 25, '2022-01-01'),
    ]

    mocker.patch.object(ContactManager, 'get_overdue_contacts',
                        return_value=database_response)


@pytest.fixture
def test_login_template_is_rendered(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data
    assert b'<form action="/" method="POST">' in response.data
    assert b'<label for="username">Username:</label>' in response.data
    assert b'<label for="password">Password:</label>' in response.data


def test_submitting_incomplete_login_form_flashes_error(client):
    request_data = {'username': '', 'password': 'testPassword'}
    response = client.post('/', data=request_data)
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data
    assert b'Username is required.' in response.data


def test_submitting_incorrect_username_flashes_error(client, mock_user_details):
    request_data = {'username': 'testUser', 'password': 'testPassword'}
    response = client.post('/', data=request_data)
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data
    assert b'Incorrect username or password.' in response.data


def test_submitting_incorrect_password_flashes_error(client, mock_user_details):
    request_data = {'username': 'ashoka', 'password': 'wrongPassword'}
    response = client.post('/', data=request_data)
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data
    assert b'Incorrect username or password.' in response.data


def test_submitting_correct_username_and_password_redirects_user_to_home(client, mock_user_details, mock_overdue_contacts):
    request_data = {'username': 'ashoka', 'password': 'testPassword'}
    response = client.post('/', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'<h1>Home - ashoka</h1>' in response.data
