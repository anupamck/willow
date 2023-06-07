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
        (1, 'Kujula Kadphises', 30, '2023-01-01'),
        (2, 'Kanishka', 25, '2022-01-01'),
    ]
    mocker.patch.object(ContactManager,
                        'get_overdue_contacts',
                        return_value=database_response
                        )


def test_template_is_rendered(client, mock_database):
    # Make assertions based on the mocked data
    response = client.get('/')
    assert response.status_code == 200
    assert b'<h1>Home</h1>' in response.data
    assert b'<table aria-label="home-table">' in response.data


def test_overdue_contacts_are_rendered(client, mock_database):
    # Make assertions based on the mocked data
    response = client.get('/')
    assert response.status_code == 200
    assert b'Kujula Kadphises' in response.data
    assert b'Kanishka' in response.data
