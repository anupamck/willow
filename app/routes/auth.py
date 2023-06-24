from flask import Blueprint, render_template, request, flash, redirect, url_for
import flask
from ..routes.db import DatabaseConnector, UserManager
import flask_login
from flask_login import UserMixin, login_user, logout_user, login_required
import os
from urllib.parse import urlparse, urljoin
import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint('auth', __name__)

users_db = os.path.join(os.getenv('DB_PATH'), "users.db")


class User(UserMixin):
    def __init__(self, username):
        self.id = username

    @staticmethod
    def get(username):
        with DatabaseConnector(database=users_db) as connector:
            user_manager = UserManager(connector)
            user_details = user_manager.get_user(username)
            if user_details is not None:
                user = User(user_details['username'])
                user.username = user_details['username']
                user.password = user_details['password']
                user.salt = user_details['salt']
                user.database = user_details['database']
                return user
            return None


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('home.get_home'))

    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        if not password:
            error = 'Password is required.'

        if error is not None:
            flash(error)
            return render_template('login.html')

        with DatabaseConnector(database=users_db) as connector:
            user_manager = UserManager(connector)
            user = User.get(username)
            if user is None:
                error = 'Incorrect username or password.'
            if not user_manager.is_password_correct(username, password):
                error = 'Incorrect username or password.'

            if error is not None:
                flash(error, 'error')
                return render_template('login.html')
            else:
                login_user(user, remember=True,
                           duration=datetime.timedelta(days=30))
                next = flask.request.args.get('next')
                if not is_safe_url(next):
                    return flask.abort(400)
                return redirect(url_for('home.get_home'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def is_safe_url(target):
    parsed_host_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        parsed_host_url.netloc == test_url.netloc
