from flask import Flask
from ..app.routes.home import home_bp
from ..app.routes.contacts import contacts_bp
from ..app.routes.interactions import interactions_bp
from ..app.routes.auth import auth_bp
import pytest
from ..app.routes.db import InteractionManager
import html
from flask_login import LoginManager
from ..app.routes.auth import User
from flask_login import login_user, logout_user
import datetime


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
        (1, "2023-06-08", "The battle of Kalinga", "I repent everything so much"),
        (2, "2023-07-08", "I'll build 80,000 Stupas",
         "So that I am not born better than a lizard in my next life"),
    ]

    database_response_edited = [
        (1, "2023-06-08", "The battle of Kalinga",
         "I repent everything so much. All those lives can never be gotten back again."),
        (2, "2023-07-08", "I'll build 80,000 Stupas",
         "So that I am not born better than a lizard in my next life"),
    ]

    user = User('ashoka')
    user.username = 'ashoka'
    user.database = "ashoka.db"

    mocker.patch.object(InteractionManager,
                        'get_interactions',
                        return_value=database_response
                        )

    mocker.patch.object(InteractionManager,
                        'get_interaction',
                        return_value=(
                            1, "2023-06-08", "The battle of Kalinga", "I repent everything so much")
                        )

    mocker.patch.object(User,
                        'get',
                        return_value=user
                        )


def test_not_logged_in_user_redirected_to_login_page(client):
    response = client.get(
        '/interactions/1/Ashoka', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data
    assert b'<h1>Login</h1>' in response.data


def test_interactions_template_is_rendered(authenticated_client, mock_database):
    response = authenticated_client.get('/interactions/1/Ashoka')
    assert response.status_code == 200
    assert b'<h1>Interactions - Ashoka</h1>' in response.data
    assert b'<table aria-label="interactions-table">' in response.data


def test_interactions_are_rendered(authenticated_client, mock_database):
    response = authenticated_client.get('/interactions/1/Ashoka')
    assert response.status_code == 200
    decoded_response_data = response.data.decode('utf-8')
    unescaped_response_data = html.unescape(decoded_response_data)
    assert b'2023-06-08' in response.data
    assert b'The battle of Kalinga' in response.data
    assert b'I repent everything so much' in response.data
    assert b'2023-07-08' in response.data
    assert "I'll build 80,000 Stupas" in unescaped_response_data
    assert b'So that I am not born better than a lizard in my next life' in response.data


def test_add_interaction_form_is_rendered(authenticated_client, mock_database):
    response = authenticated_client.get('/interactions/1/Ashoka')
    assert response.status_code == 200
    assert b'<h1>Interactions - Ashoka</h1>' in response.data
    assert b'The battle of Kalinga' in response.data
    assert b'I repent everything so much' in response.data
    assert b'2023-07-08' in response.data
    assert b'So that I am not born better than a lizard in my next life' in response.data


def test_error_thrown_when_incomplete_interaction_added(authenticated_client, mock_database):
    request_data = {'date': '2023-06-08',
                    'title': 'The battle of Kalinga', 'notes': '', 'person_id': '1', 'contact_name': 'Ashoka'}
    response = authenticated_client.post(
        '/add_interaction/1/Ashoka', data=request_data)
    assert response.status_code == 200
    assert b'Title and notes are required' in response.data


def test_redirects_to_interactions_page_when_interaction_added_successfully(authenticated_client, mock_database):
    request_data = {'date': '2023-06-08',
                    'title': 'The battle of Kalinga', 'notes': 'I repent everything so much', 'person_id': '1', 'contact_name': 'Ashoka'}
    response = authenticated_client.post(
        '/add_interaction/1/Ashoka', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'<h1>Interactions - Ashoka</h1>' in response.data


def test_edit_interaction_form_is_rendered(authenticated_client, mock_database):
    response = authenticated_client.get('/edit_interaction/1/1/Ashoka')
    assert response.status_code == 200
    assert b'Edit Interaction' in response.data
    assert b'<input type="date" id="date" name="date" value="2023-06-08" required>' in response.data
    assert b'<input type="text" id="title" name="title" value="The battle of Kalinga" required>' in response.data
    assert b'<textarea id="notes" name="notes" rows="10" cols="50" required>I repent everything so much</textarea>' in response.data
    assert b'<button type="submit">Save Changes</button>' in response.data


def test_error_thrown_when_interaction_edited_without_title(authenticated_client, mock_database):
    request_data = {'id': 1, 'date': '2023-06-08',
                    'title': '', 'notes': 'I repent everything so much', 'person_id': '1', 'contact_name': 'Ashoka'}
    response = authenticated_client.post(
        '/edit_interaction/1/1/Ashoka', data=request_data)
    assert response.status_code == 200
    assert b'Title and notes are required.' in response.data


def test_redirects_to_interaction_form_when_interaction_edited_successfully(authenticated_client, mock_database):
    request_data = {'id': 1, 'date': '2023-06-08',
                    'title': 'The battle of Kalinga', 'notes': 'I repent everything so much. All those lives can never be gotten back again.', 'person_id': '1', 'contact_name': 'Ashoka'}
    response = authenticated_client.post(
        '/edit_interaction/1/1/Ashoka', data=request_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'<h1>Interactions - Ashoka</h1>' in response.data


def test_delete_interaction(authenticated_client, mock_database):
    response = authenticated_client.get(
        '/delete_interaction/1/1/Ashoka', follow_redirects=True)
    assert response.status_code == 200
    assert b'<h1>Interactions - Ashoka</h1>' in response.data


def test_add_interaction_is_prefilled_with_todays_date(authenticated_client, mock_database):
    response = authenticated_client.get('/add_interaction/1/Ashoka')
    assert response.status_code == 200
    today = datetime.date.today().strftime("%Y-%m-%d")
    date_field = f'<input type="date" id="date" name="date" value="{today}" required>'
    assert date_field.encode() in response.data
