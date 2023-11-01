from flask import Flask
from ..app.routes.auth import auth_bp, TokenManager
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
from ..app.routes.email import EmailClient


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
def mock_user_details(mocker):
    mocker.patch('sqlite3.connect')

    # prepare mock responses
    salt = b'$2b$12$VUEfecQgohf4CKkB2loTKO'
    password_hashed = bcrypt.hashpw(
        "testPassword".encode('utf-8'), salt)

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
    mocker.patch.object(UserManager, 'get_user_by_email',
                        return_value=user_details_ashoka)


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
def mock_valid_password_reset_token(mocker):
    mocker.patch.object(TokenManager, 'verify_token',
                        return_value='ashoka')


@pytest.fixture
def mock_send_email(mocker):
    mock = mocker.patch.object(EmailClient, 'send_email', return_value=None)
    return mock


@pytest.fixture
def mock_move_mail_to_sent_items(mocker):
    mock = mocker.patch.object(
        EmailClient, 'move_mail_to_sent_items', return_value=None)
    return mock


@pytest.fixture
def mock_change_password(mocker):
    mock = mocker.patch.object(
        UserManager, 'change_password', return_value=None)
    return mock


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


def test_login_template_is_rendered(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<h2>Login</h2>' in response.data
    assert b'<form action="/" method="POST">' in response.data
    assert b'<label for="username">Username:</label>' in response.data
    assert b'<label for="password">Password:</label>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    login_button = soupHtml.find('button', string='Login')
    assert login_button is not None
    register_button = soupHtml.find('button', string='Register')
    assert register_button is not None
    forgot_password_link = soupHtml.find('a', string='Forgot password?')
    assert forgot_password_link is not None


def test_submitting_incomplete_login_form_flashes_error(client):
    request_data = {'username': '', 'password': 'testPassword'}
    response = client.post('/', data=request_data)
    assert response.status_code == 200
    assert b'<h2>Login</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    assert 'Username is required.' in error_message.string


def test_submitting_incorrect_username_flashes_error(client, mock_user_details):
    request_data = {'username': 'testUser', 'password': 'testPassword'}
    response = client.post('/', data=request_data)
    assert response.status_code == 200
    assert b'<h2>Login</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    assert 'Incorrect username or password.' in error_message.string


def test_submitting_incorrect_password_flashes_error(client, mock_user_details):
    request_data = {'username': 'ashoka', 'password': 'wrongPassword'}
    response = client.post('/', data=request_data)
    assert response.status_code == 200
    assert b'<h2>Login</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    assert 'Incorrect username or password.' in error_message.string


def test_submitting_correct_username_and_password_redirects_user_to_home(client, mock_user_details, mock_overdue_contacts):
    request_data = {'username': 'ashoka', 'password': 'testPassword'}
    response = client.post('/', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>Long time no speak</h2>' in response.data


def test_logged_in_user_is_redirected_to_homepage(authenticated_client):
    response = authenticated_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>Long time no speak</h2>' in response.data


def test_logged_in_user_is_redirected_to_homepage_on_accesssing_forgot_password_url(authenticated_client):
    response = authenticated_client.get(
        '/forgot_password', follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>Long time no speak</h2>' in response.data


def test_forgot_password_form_is_rendered(client):
    response = client.get('/forgot_password')
    assert response.status_code == 200
    print(response.data)
    assert b'<title>Willow - Forgot Password</title>' in response.data
    assert b'<h2>Forgot password?</h2>' in response.data
    assert b'<form action="/forgot_password" method="POST">' in response.data
    assert b'<label for="email">E-mail:</label>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    submit_button = soupHtml.find('button', string='Submit')
    assert submit_button is not None


def test_submitting_incomplete_forgot_password_form_flashes_error(client):
    request_data = {'email': ''}
    response = client.post('/forgot_password', data=request_data)
    assert response.status_code == 200
    assert b'<h2>Forgot password?</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    assert 'E-mail is required.' in error_message.string


def test_submitting_invalid_email_flashes_error(client):
    request_data = {'email': 'agmail.com'}
    response = client.post('/forgot_password', data=request_data)
    assert response.status_code == 200
    assert b'<h2>Forgot password?</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    assert 'E-mail is invalid.' in error_message.string


def test_submitting_unregistered_email_flashes_error(client):
    request_data = {'email': 'bimbisara@maghada.com'}
    response = client.post('/forgot_password', data=request_data)
    assert response.status_code == 200
    assert b'<h2>Forgot password?</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    assert 'E-mail is not registered.' in error_message.string


def test_password_reset_email_confirmation_is_displayed(client, mock_send_email, mock_move_mail_to_sent_items):
    request_data = {'email': 'ashoka@maghada.com'}
    response = client.post(
        '/forgot_password', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>Login</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    success_message = soupHtml.find('div', class_='flash-success')
    assert success_message is not None
    assert 'A password reset link has been sent to your e-mail address.' in success_message.string


def test_error_is_displayed_when_reset_token_is_invalid(client):
    response = client.get('/reset_password/invalid_token',
                          follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>Login</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    assert 'Invalid token. Please try again.' in error_message.string


def test_password_reset_form_is_rendered_with_valid_token(client, mock_valid_password_reset_token):
    response = client.get('/reset_password/valid_token')
    assert response.status_code == 200
    assert b'<title>Willow - Reset Password</title>' in response.data
    assert b'<h2>Reset password</h2>' in response.data
    assert b'<form action="/reset_password/valid_token" method="POST">' in response.data
    assert b'<label for="password">New password:</label>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    submit_button = soupHtml.find('button', string='Submit')
    assert submit_button is not None


def test_submitting_incomplete_password_reset_form_flashes_error(client, mock_valid_password_reset_token):
    request_data = {'password': ''}
    response = client.post('/reset_password/valid_token',
                           data=request_data)
    assert response.status_code == 200
    assert b'<h2>Reset password</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    print(error_message.string)
    assert 'Password is required.' in error_message.string


def test_success_message_is_displayed_on_submitting_valid_password_reset_form(client, mock_valid_password_reset_token, mock_change_password):
    request_data = {'password': 'newPassword'}
    response = client.post('/reset_password/valid_token',
                           data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>Login</h2>' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    success_message = soupHtml.find('div', class_='flash-success')
    assert success_message is not None
    assert 'Password changed successfully. Please login.' in success_message.string
