from flask import Flask
from ..app.routes.home import home_bp
from ..app.routes.contacts import contacts_bp
from ..app.routes.interactions import interactions_bp
import pytest
from ..app.routes.db import InteractionManager
import html


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
        (1, "2023-06-08", "The battle of Kalinga", "I repent everything so much"),
        (2, "2023-07-08", "I'll build 80,000 Stupas",
         "So that I am not born better than a lizard in my next life"),
    ]
    mocker.patch.object(InteractionManager,
                        'get_interactions',
                        return_value=database_response
                        )

    mocker.patch.object(InteractionManager,
                        'get_interaction',
                        return_value=(
                            1, "2023-06-08", "The battle of Kalinga", "I repent everything so much")
                        )


def test_interactions_template_is_rendered(client, mock_database):
    response = client.get('/interactions/1/Ashoka')
    assert response.status_code == 200

    assert b'<h1>Interactions - Ashoka</h1>' in response.data
    assert b'<table aria-label="interactions-table">' in response.data


def test_interactions_are_rendered(client, mock_database):
    response = client.get('/interactions/1/Ashoka')
    assert response.status_code == 200
    decoded_response_data = response.data.decode('utf-8')
    unescaped_response_data = html.unescape(decoded_response_data)
    assert b'2023-06-08' in response.data
    assert b'The battle of Kalinga' in response.data
    assert b'I repent everything so much' in response.data
    assert b'2023-07-08' in response.data
    assert "I'll build 80,000 Stupas" in unescaped_response_data
    assert b'So that I am not born better than a lizard in my next life' in response.data


def test_add_interaction_form_is_rendered(client, mock_database):
    response = client.get('/interactions/1/Ashoka')
    assert response.status_code == 200
    print(response.data)
    assert b'<h1>Interactions - Ashoka</h1>' in response.data
    assert b'The battle of Kalinga' in response.data
    assert b'I repent everything so much' in response.data
    assert b'2023-07-08' in response.data
    assert b'So that I am not born better than a lizard in my next life' in response.data


def test_error_thrown_when_incomplete_interaction_added(client, mock_database):
    request_data = {'date': '2023-06-08',
                    'title': 'The battle of Kalinga', 'notes': '', 'person_id': '1', 'contact_name': 'Ashoka'}
    response = client.post('/add_interaction/1/Ashoka', data=request_data)
    assert response.status_code == 200
    print(response.data)
    assert b'Title and notes are required' in response.data


def test_redirects_to_interactions_page_when_interaction_added_successfully(client, mock_database):
    request_data = {'date': '2023-06-08',
                    'title': 'The battle of Kalinga', 'notes': 'I repent everything so much', 'person_id': '1', 'contact_name': 'Ashoka'}
    response = client.post('/add_interaction/1/Ashoka', data=request_data)
    assert response.status_code == 201
    assert b'You should be redirected automatically to the target URL: <a href="/interactions/1/Ashoka">' in response.data


def test_edit_interaction_form_is_rendered(client, mock_database):
    response = client.get('/edit_interaction/1/1/Ashoka')
    assert response.status_code == 200
    print(response.data)
    assert b'Edit Interaction' in response.data
    assert b'<input type="date" id="date" name="date" value="2023-06-08" required>' in response.data
    assert b'<input type="text" id="title" name="title" value="The battle of Kalinga" required>' in response.data
    assert b'<textarea id="notes" name="notes" rows="10" cols="50" required>I repent everything so much</textarea>' in response.data
    assert b'<button type="submit">Save Changes</button>' in response.data


def test_error_thrown_when_interaction_edited_without_title(client, mock_database):
    request_data = {'id': 1, 'date': '2023-06-08',
                    'title': '', 'notes': 'I repent everything so much', 'person_id': '1', 'contact_name': 'Ashoka'}
    response = client.post('/edit_interaction/1/1/Ashoka', data=request_data)
    assert response.status_code == 200
    print(response.data)
    assert b'Title and notes are required.' in response.data


def test_redirects_to_interaction_form_when_interaction_edited_successfully(client, mock_database):
    request_data = {'id': 1, 'date': '2023-06-08',
                    'title': 'The battle of Kalinga', 'notes': 'I repent everything so much. All those lives can never be gotten back again.', 'person_id': '1', 'contact_name': 'Ashoka'}
    response = client.post('/edit_interaction/1/1/Ashoka', data=request_data)
    assert response.status_code == 201
    assert b'You should be redirected automatically to the target URL: <a href="/interactions/1/Ashoka">' in response.data


def test_delete_interaction(client, mock_database):
    response = client.get('/delete_interaction/1/1/Ashoka')
    assert response.status_code == 200
    assert b'You should be redirected automatically to the target URL: <a href="/interactions/1/Ashoka">' in response.data
