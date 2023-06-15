from flask import Flask
from ..app.routes.auth import auth_bp
from ..app.routes.home import home_bp
from ..app.routes.contacts import contacts_bp
import pytest
from ..app.routes.db import UserManager
import bcrypt
from flask_login import LoginManager
from ..app.routes.auth import User


@pytest.fixture
def app():
    app = Flask(__name__, template_folder='../app/templates')
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(contacts_bp)
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
def mock_database(mocker):
    mocker.patch('mysql.connector.connect')
    salt = '$2b$12$VUEfecQgohf4CKkB2loTKO'
    password_hashed = bcrypt.hashpw(
        "testPassword".encode('utf-8'), salt.encode('utf-8')).decode('utf-8')
    user_details = {
        'username': 'ashoka',
        'password': password_hashed,
        'salt': salt,
        'email': 'ashoka@maghada.com',
        'config': {"user": "u936540649_willowTest", "password": "$2b$12$QGyilzNz6OP8ugyW4EtW9OBQzfOfa6X8k1SWTaXdhLQOeqC9rfyQa",
                   "host": "srv976.hstgr.io", "database": "u936540649_willowTest"}
    }

    # Define the side_effect function
    def side_effect(username):
        if username == "ashoka":
            return user_details
        else:
            return None

    # Patch the get_user method with the updated side_effect
    mocker.patch.object(UserManager, 'get_user', side_effect=side_effect)


def test_login_template_is_rendered(client):
    response = client.get('/')
    assert response.status_code == 200
    print(response.data)
    assert b'<h1>Login</h1>' in response.data
    assert b'<form action="/" method="POST">' in response.data
    assert b'<input type="text" name="username" required>' in response.data
    assert b'<input type="password" name="password" required>' in response.data


def test_submitting_incomplete_login_form_flashes_error(client):
    request_data = {'username': '', 'password': 'testPassword'}
    response = client.post('/', data=request_data)
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data
    assert b'Username is required.' in response.data


def test_submitting_incorrect_username_flashes_error(client, mock_database):
    request_data = {'username': 'testUser', 'password': 'testPassword'}
    response = client.post('/', data=request_data)
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data
    assert b'Incorrect username or password.' in response.data


@pytest.mark.todo
def test_submitting_incorrect_password_flashes_error(client, mock_database):
    pass


def test_submitting_correct_username_and_password_redirects_user_to_home(client, mock_database):
    request_data = {'username': 'ashoka', 'password': 'testPassword'}
    response = client.post('/', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    print(response.data)
    assert b'<h1>Home - ashoka</h1>' in response.data
