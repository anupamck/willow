from flask import Flask
from ..app.routes.home import home_bp
from ..app.routes.contacts import contacts_bp
from ..app.routes.interactions import interactions_bp
from ..app.routes.auth import auth_bp
from ..app.routes.account import account_bp
import pytest
from ..app.routes.db import ContactManager
from flask_login import LoginManager
from ..app.routes.auth import User
from flask_login import login_user, logout_user
from bs4 import BeautifulSoup


@pytest.fixture
def app():
    app = Flask(__name__, template_folder='../app/templates')
    app.register_blueprint(home_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(interactions_bp)
    app.register_blueprint(auth_bp)
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
        login_user(user)

        yield client

        # Perform any necessary cleanup after the test
        logout_user()


@pytest.fixture
def mock_database(mocker):
    mocker.patch('sqlite3.connect')

    # Mock the return value of the get_overdue_contacts method
    database_response = [
        (1, 'Ashoka', 30),
        (2, 'Bimbisara', 25),
    ]

    user = User('ashoka')
    user.username = 'ashoka'
    user.database = "ashoka.db"

    mocker.patch.object(ContactManager,
                        'get_contacts',
                        return_value=database_response
                        )

    mocker.patch.object(ContactManager,
                        'get_contact',
                        return_value=(1, 'Ashoka', 30)
                        )

    mocker.patch.object(User,
                        'get',
                        return_value=user
                        )


@pytest.fixture
def mock_database_no_contacts(mocker):
    mocker.patch('sqlite3.connect')

    # Mock the return value of the get_overdue_contacts method
    database_response = []

    user = User('ashoka')
    user.username = 'ashoka'
    user.database = "ashoka.db"

    mocker.patch.object(ContactManager,
                        'get_contacts',
                        return_value=database_response
                        )

    mocker.patch.object(ContactManager,
                        'get_contact',
                        return_value=None
                        )

    mocker.patch.object(User,
                        'get',
                        return_value=user
                        )


def test_not_logged_in_user_redirected_to_login_page(client):
    response = client.get('/contacts', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data
    assert b'<h2>Login</h2>' in response.data


def test_template_is_rendered(authenticated_client, mock_database):
    response = authenticated_client.get('/contacts')
    assert response.status_code == 200
    assert b'<h2>My Contacts</h2>' in response.data
    assert b'<table aria-label="contacts-table">' in response.data


def test_contacts_are_rendered(authenticated_client, mock_database):
    response = authenticated_client.get('/contacts')
    assert response.status_code == 200
    assert b'Ashoka' in response.data
    assert b'Bimbisara' in response.data


def test_add_contact_form_is_rendered(authenticated_client, mock_database):
    response = authenticated_client.get('/add_contact')
    assert response.status_code == 200
    assert b'<title>Willow - Contact Form</title>' in response.data
    assert b'Add Contact' in response.data
    assert b'<input type="text" id="name" name="name" value="" required>' in response.data
    assert b'<input type="number" id="frequency" name="frequency" value="" required min="1">' in response.data
    assert b'<button type="submit">Save Changes</button>' in response.data


def test_error_thrown_when_contact_added_without_frequency(authenticated_client, mock_database):
    request_data = {'name': 'Ashoka', 'frequency': ''}
    response = authenticated_client.post('/add_contact', data=request_data)
    assert response.status_code == 200
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    assert 'Frequency is required' in error_message.string


def test_redirects_to_contacts_page_when_contact_added_successfully(authenticated_client, mock_database):
    request_data = {'name': 'Ashoka', 'frequency': '30'}
    response = authenticated_client.post(
        '/add_contact', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>My Contacts</h2>' in response.data


def test_edit_contact_form_is_rendered(authenticated_client, mock_database):
    response = authenticated_client.get('/edit_contact/1')
    assert response.status_code == 200
    assert b'<title>Willow - Contact Form</title>' in response.data
    assert b'Edit Contact' in response.data
    assert b'<input type="text" id="name" name="name" value="Ashoka" required>' in response.data
    assert b'<input type="number" id="frequency" name="frequency" value="30" required min="1">' in response.data
    assert b'<button type="submit">Save Changes</button>' in response.data


def test_error_thrown_when_contact_edited_without_frequency(authenticated_client, mock_database):
    request_data = {'name': 'Ashoka', 'frequency': ''}
    response = authenticated_client.post('/edit_contact/1', data=request_data)
    assert response.status_code == 200
    soupHtml = BeautifulSoup(response.data, 'html.parser')
    error_message = soupHtml.find('div', class_='flash-error')
    assert error_message is not None
    assert 'Frequency is required' in error_message.string


def test_redirects_to_contact_form_when_contact_edited_successfully(authenticated_client, mock_database):
    request_data = {'name': 'Ashoka', 'frequency': '30'}
    response = authenticated_client.post(
        '/edit_contact/1', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>My Contacts</h2>' in response.data


def test_delete_contact(authenticated_client, mock_database):
    response = authenticated_client.get(
        '/delete_contact/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'<h2>My Contacts</h2>' in response.data


def test_no_contacts(authenticated_client, mock_database_no_contacts):
    response = authenticated_client.get('/contacts')
    assert response.status_code == 200
    assert b'<h2>My Contacts</h2>' in response.data
    assert b"You don't have any contacts" in response.data
    assert b'To add a new contact, click <a href="/add_contact">here' in response.data
