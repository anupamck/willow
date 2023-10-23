from flask import Flask
import pytest
from ..app.routes.home import home_bp
from ..app.routes.contacts import contacts_bp
from ..app.routes.interactions import interactions_bp
from ..app.routes.auth import auth_bp
from ..app.routes.account import account_bp
from flask_login import LoginManager
from ..app.routes.auth import User
from flask_login import login_user, logout_user
from bs4 import BeautifulSoup
from ..app.routes.db import UserManager
import bcrypt
import os


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
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'

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
        user.email = 'ashoka@maghada.com'
        login_user(user)

        yield client

        # Perform any necessary cleanup after the test
        logout_user()


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

    # Patch the get_user method with the updated side_effect
    mocker.patch.object(UserManager, 'get_user',
                        return_value=user_details_ashoka)


@pytest.fixture
def mock_delete_user_database(mocker):
    mocker.patch.object(os, 'remove',
                        return_value=None)


@pytest.fixture
def mock_delete_user(mocker):
    mocker.patch.object(UserManager, 'delete_user',
                        return_value=None)


def test_user_account_template_is_rendered(authenticated_client):
    response = authenticated_client.get(
        '/account', follow_redirects=True)
    assert response.status_code == 200
    assert b'User Account' in response.data
    assert b'Username: ashoka' in response.data
    assert b'E-mail: ashoka@maghada.com' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    delete_button = soupHtml.find('button', string='Delete Account')
    assert delete_button is not None
    change_password_button = soupHtml.find('button', string='Change Password')
    assert change_password_button is not None


def test_change_password_form_is_rendered(authenticated_client):
    response = authenticated_client.get(
        '/change_password', follow_redirects=True)
    assert response.status_code == 200
    assert b'Current password' in response.data
    assert b'New password' in response.data
    assert b'Confirm new password' in response.data
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    change_password_button = soupHtml.find('button', string='Change Password')
    assert change_password_button is not None


def test_error_thrown_when_form_submitted_without_current_password(authenticated_client):
    request_data = {'current_password': '',
                    'new_password': 'new_password',
                    'confirm_password': 'new_password'}
    response = authenticated_client.post(
        '/change_password', data=request_data, follow_redirects=True)
    # assert response.status_code == 200
    assert b'Current password is required' in response.data


def test_error_thrown_when_new_passwords_do_not_match(authenticated_client):
    request_data = {'current_password': 'password',
                    'new_password': 'new_password',
                    'confirm_password': 'new_password1'}
    response = authenticated_client.post(
        '/change_password', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'New password and confirm new password must match' in response.data


def test_error_thrown_when_form_submitted_without_new_password(authenticated_client):
    request_data = {'current_password': 'password',
                    'new_password': '',
                    'confirm_password': 'new_password'}
    response = authenticated_client.post(
        '/change_password', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'New password is required' in response.data


def test_error_thrown_when_form_submitted_without_confirm_password(authenticated_client):
    request_data = {'current_password': 'password',
                    'new_password': 'new_password',
                    'confirm_password': ''}
    response = authenticated_client.post(
        '/change_password', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Confirm new password is required' in response.data


def test_error_thrown_when_old_password_is_incorrect(authenticated_client,  mock_user_details):
    request_data = {'current_password': 'password',
                    'new_password': 'new_password',
                    'confirm_password': 'new_password'}
    response = authenticated_client.post(
        '/change_password', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Current password is incorrect' in response.data


def test_user_can_change_password(authenticated_client, mock_user_details):
    request_data = {'current_password': 'testPassword',
                    'new_password': 'new_password',
                    'confirm_password': 'new_password'}
    response = authenticated_client.post(
        '/change_password', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password changed successfully' in response.data


def test_user_can_delete_their_account(authenticated_client, mock_delete_user, mock_delete_user_database):
    response = authenticated_client.post(
        '/delete_user', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Account deleted successfully' in response.data
