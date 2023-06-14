from flask import Flask
from ..app.routes.login import login_bp
import pytest


@pytest.fixture
def app():
    app = Flask(__name__, template_folder='../app/templates')
    app.register_blueprint(login_bp)
    app.config['TESTING'] = True
    app.secret_key = 'test'
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_login_template_is_rendered(client):
    response = client.get('/login')
    assert response.status_code == 200
    print(response.data)
    assert b'<h1>Login</h1>' in response.data
    assert b'<form action="/login" method="POST">' in response.data
    assert b'<input type="text" name="username" required>' in response.data
    assert b'<input type="password" name="password" required>' in response.data


def test_submitting_incomplete_login_form_flashes_error(client):
    request_data = {'username': '', 'password': 'testPassword'}
    response = client.post('/login', data=request_data)
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data
    assert b'Username is required.' in response.data


def test_submitting_incorrect_username_or_password_flashes_error(client):
    request_data = {'username': 'testUser', 'password': 'testPassword'}
    response = client.post('/login', data=request_data)
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data
    assert b'Incorrect username or password.' in response.data
