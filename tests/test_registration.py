'''Tests for a page that handles user registration. 
The tests cases should include:
- The registration page and form is rendered correctly
- Mandatory fields are required
- Error is thrown when the username is not unique
- Error is thrown when the email is not unique
- Error is thrown when the passwords do not match
- Error is thrown when the email address is invalid
- The user can register successfully and is redirected to the login page
- Logged in user is redirected to home page when they try to access the registration page
'''

from flask import Flask
from ..app.routes.auth import auth_bp
from ..app.routes.home import home_bp
from ..app.routes.contacts import contacts_bp
from ..app.routes.interactions import interactions_bp
from ..app.routes.account import account_bp
import pytest
from ..app.routes.db import UserManager, ContactManager
import bcrypt
from flask_login import LoginManager, login_user, logout_user
from ..app.routes.auth import User
from bs4 import BeautifulSoup


@pytest.fixture
def app():
    app = Flask(__name__, template_folder='../app/templates')
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(interactions_bp)
    app.register_blueprint(account_bp)
    app.config['TESTING'] = True
    app.secret_key = 'test'

    # Initialize the LoginManager and associate it with the app
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Configure the login view and endpoint
    login_manager.login_view = 'auth.login'

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
        user = User('ashoka')
        user.username = 'ashoka'
        login_user(user)

        yield client

        # Perform any necessary cleanup after the test
        logout_user()


@pytest.fixture
def mock_user(mocker):
    mocker.patch('sqlite3.connect')

    # Mock the return value of users in the database
    database_response = [
        ('mockUser', 'mock@email.com')
    ]

    mocker.patch.object(UserManager, 'get_user',
                        return_value=database_response)


@pytest.fixture
def mock_email_registered(mocker):
    mocker.patch('sqlite3.connect')

    mocker.patch.object(UserManager, 'is_email_id_already_registered',
                        return_value=True)


@pytest.fixture
def mock_add_user(mocker):
    mocker.patch('sqlite3.connect')

    mocker.patch.object(UserManager, 'add_user',
                        return_value=None)

    mocker.patch.object(UserManager, 'initialize_user_db',
                        return_value=None)


def test_should_render_registration_page(client):
    # Test that the registration page is rendered correctly
    response = client.get('/register')
    assert response.status_code == 200
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    heading = soupHtml.find('h2', string='Registration')
    assert heading is not None
    assert b"Username" in response.data
    assert b"Password" in response.data
    assert b"E-mail" in response.data
    register_button = soupHtml.find('button', string='Register')
    assert register_button is not None


def test_logged_in_user_is_redirected_to_home_page(authenticated_client):
    response = authenticated_client.get(
        '/register', follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>Long time no speak</h2>' in response.data


def test_error_is_displayed_when_username_is_blank(client):
    # Test that an error is thrown when the username is blank
    request_data = {'username': '', 'password': 'testPassword',
                    'confirm_password': 'testPassword', 'email': 'test@email.com'}
    response = client.post('/register', data=request_data)
    assert response.status_code == 200
    assert b"Username is required" in response.data


def test_error_is_displayed_when_email_is_blank(client):
    request_data = {'username': 'testUser', 'password': 'testPassword',
                    'confirm_password': 'testPassword', 'email': ''}
    response = client.post('/register', data=request_data)
    assert response.status_code == 200
    assert b"E-mail is required" in response.data


def test_error_is_displayed_when_email_is_invalid(client):
    request_data = {'username': 'testUser', 'password': 'testPassword',
                    'confirm_password': 'testPassword', 'email': 'testemail.com'}
    response = client.post('/register', data=request_data)
    assert response.status_code == 200
    assert b"E-mail is invalid" in response.data


def test_error_is_displayed_when_password_is_blank(client):
    request_data = {'username': 'testUser', 'password': '',
                    'confirm_password': 'testPassword', 'email': 'test@email.com'}
    response = client.post('/register', data=request_data)
    assert response.status_code == 200
    assert b"Password is required" in response.data


def test_error_is_displayed_when_passwords_do_not_match(client):
    request_data = {'username': 'testUser', 'password': 'testPassword',
                    'confirm_password': 'testPassword2', 'email': 'test@mail.com'}
    response = client.post('/register', data=request_data)
    assert response.status_code == 200
    assert b"Password and confirm password must match" in response.data


def test_error_is_displayed_when_username_already_exists(client, mock_user):
    request_data = {'username': 'mockUser', 'password': 'testPassword',
                    'confirm_password': 'testPassword', 'email': 'test@mail.com'}
    response = client.post('/register', data=request_data)
    assert response.status_code == 200
    assert b"Username is already taken" in response.data


def test_error_is_displayed_when_email_already_registered(client, mock_email_registered):
    request_data = {'username': 'ashoka2', 'password': 'testPassword',
                    'confirm_password': 'testPassword', 'email': 'mock@email.com'}
    response = client.post('/register', data=request_data)
    assert response.status_code == 200
    assert b"This e-mail address is already registered" in response.data


def test_user_can_register_and_is_redirected_to_login(client, mock_add_user):
    request_data = {'username': 'testUser', 'password': 'testPassword',
                    'confirm_password': 'testPassword', 'email': 'mock@email.com'}
    response = client.post(
        '/register', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>Login</h2>' in response.data
    assert b'Account created successfully. Please login.' in response.data
