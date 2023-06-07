from flask import Flask
from ..app.routes.home import home_bp
from ..app.routes.contacts import contacts_bp
from ..app.routes.interactions import interactions_bp
import pytest
from ..app.routes.db import ContactManager


@pytest.fixture
def app():
    app = Flask(__name__, template_folder='../app/templates')
    app.register_blueprint(home_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(interactions_bp)
    app.config['TESTING'] = True
    app.secret_key = 'test'
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_database(mocker):
   # Patch the entire mysql.connector module to mock database interactions
    mocker.patch('mysql.connector.connect')

    # Mock the return value of the get_overdue_contacts method
    database_response = [
        (1, 'Ashoka', 30),
        (2, 'Bimbisara', 25),
    ]
    mocker.patch.object(ContactManager,
                        'get_contacts',
                        return_value=database_response
                        )

    mocker.patch.object(ContactManager,
                        'add_contact',
                        return_value=None
                        )

    mocker.patch.object(ContactManager,
                        'get_contact',
                        return_value=(1, 'Ashoka', 30)
                        )
    mocker.patch.object(ContactManager,
                        'edit_contact',
                        return_value=None
                        )


def test_template_is_rendered(client, mock_database):
    response = client.get('/contacts')
    assert response.status_code == 200
    assert b'<h1>My Contacts</h1>' in response.data
    assert b'<table aria-label="contacts-table">' in response.data


def test_contacts_are_rendered(client, mock_database):
    response = client.get('/contacts')
    assert response.status_code == 200
    assert b'Ashoka' in response.data
    assert b'Bimbisara' in response.data


def test_add_contact_form_is_rendered(client, mock_database):
    response = client.get('/add_contact')
    assert response.status_code == 200
    print(response.data)
    assert b'<title>Willow - Contact Form</title>' in response.data
    assert b'Add Contact' in response.data
    assert b'<input type="text" id="name" name="name" value="" required>' in response.data
    assert b'<input type="number" id="frequency" name="frequency" value="" required min="1">' in response.data
    assert b'<button type="submit">Save Changes</button>' in response.data


def test_error_thrown_when_contact_added_without_frequency(client, mock_database):
    request_data = {'name': 'Ashoka', 'frequency': ''}
    response = client.post('/add_contact', data=request_data)
    assert response.status_code == 200
    assert b'Frequency is required' in response.data


def test_redirects_to_contact_form_when_contact_added_successfully(client, mock_database):
    request_data = {'name': 'Ashoka', 'frequency': '30'}
    response = client.post('/add_contact', data=request_data)
    assert response.status_code == 201
    assert b'You should be redirected automatically to the target URL: <a href="/contacts">' in response.data


def test_edit_contact_form_is_rendered(client, mock_database):
    response = client.get('/edit_contact/1')
    assert response.status_code == 200
    assert b'<title>Willow - Contact Form</title>' in response.data
    assert b'Edit Contact' in response.data
    assert b'<input type="text" id="name" name="name" value="Ashoka" required>' in response.data
    assert b'<input type="number" id="frequency" name="frequency" value="30" required min="1">' in response.data
    assert b'<button type="submit">Save Changes</button>' in response.data


def test_error_thrown_when_contact_edited_without_frequency(client, mock_database):
    request_data = {'name': 'Ashoka', 'frequency': ''}
    response = client.post('/edit_contact/1', data=request_data)
    assert response.status_code == 200
    assert b'Frequency is required' in response.data


def test_redirects_to_contact_form_when_contact_edited_successfully(client, mock_database):
    request_data = {'name': 'Ashoka', 'frequency': '30'}
    response = client.post('/edit_contact/1', data=request_data)
    assert b'You should be redirected automatically to the target URL: <a href="/contacts">' in response.data


def test_delete_contact(client, mock_database):
    response = client.get('/delete_contact/1')
    assert b'You should be redirected automatically to the target URL: <a href="/contacts">' in response.data
