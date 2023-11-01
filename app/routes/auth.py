from flask import Blueprint, render_template, request, flash, redirect, url_for
import flask
from ..routes.db import DatabaseConnector, UserManager
import flask_login
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
import os
from urllib.parse import urlparse, urljoin
import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import re
from ..routes.email import EmailClient
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

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
                user.email = user_details['email']
                return user
            return None


class TokenManager:
    def __init__(self, secret_key=os.getenv('SECRET_KEY_TOKEN')):
        self.secret_key = secret_key
        self.serializer = Serializer(self.secret_key)

    def generate_token(self, username):
        return self.serializer.dumps({'username': username})

    def verify_token(self, token, max_age=3600):
        try:
            data = self.serializer.loads(token, max_age=max_age)
        except SignatureExpired:
            # Token has expired
            return None
        except BadSignature:
            # Token is invalid
            return None
        return data['username']


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
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
            flash(error, 'error')
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


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.get_home'))

    if request.method == 'GET':
        return render_template('registration.html')

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Write me a regex pattern to match emails
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        error = None
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'E-mail is required.'
        # Write me a regex to validate email addresses
        elif not re.match(email_pattern, email):
            error = 'E-mail is invalid.'
        elif not password:
            error = 'Password is required.'

        if error is not None:
            flash(error, 'error')
            return render_template('registration.html')

        with DatabaseConnector(database=users_db) as connector:
            user_manager = UserManager(connector)
            if user_manager.get_user(username) is not None:
                error = 'Username is already taken.'
            elif user_manager.is_email_id_already_registered(email):
                error = 'This e-mail address is already registered.'

            if error is not None:
                flash(error, 'error')
                return render_template('registration.html')
            else:
                user_manager.add_user(username, password,
                                      email, username + ".db")
            new_user_db_path = os.path.join(
                os.getenv('DB_PATH'), username + '.db')
            with DatabaseConnector(database=new_user_db_path) as connector:
                user_manager = UserManager(connector)
                user_manager.initialize_user_db()
            flash('Account created successfully. Please login.', 'success')
            return redirect(url_for('auth.login'))


@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('home.get_home'))

    if request.method == 'GET':
        return render_template('forgotPasswordForm.html')

    elif request.method == 'POST':
        email = request.form['email']

        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        error = None
        if not email:
            error = 'E-mail is required.'
        elif not re.match(email_pattern, email):
            error = 'E-mail is invalid.'

        if error is not None:
            flash(error, 'error')
            return render_template('forgotPasswordForm.html')

        with DatabaseConnector(database=users_db) as connector:
            user_manager = UserManager(connector)
            if not user_manager.is_email_id_already_registered(email):
                error = 'E-mail is not registered.'
            if error is not None:
                flash(error, 'error')
                return render_template('forgotPasswordForm.html')

            else:
                user = user_manager.get_user_by_email(email)
                tokenManager = TokenManager()
                token = tokenManager.generate_token(user['username'])
                # Send password reset link via email
                email_client = EmailClient(os.getenv('EMAIL_USERNAME'),
                                           os.getenv('EMAIL_PASSWORD'))
                email_body = f'Click on the link to reset your password: {url_for("auth.reset_password", token=token, _external=True)}'
                email_client.send_email(
                    email, 'Willow - Password reset link', email_body)
                email_client.move_mail_to_sent_items(
                    email, 'Willow - Password reset link', email_body)
                flash(
                    'A password reset link has been sent to your e-mail address.', 'success')
                return redirect(url_for('auth.login'))


@auth_bp.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home.get_home'))

    if request.method == 'GET':
        tokenManager = TokenManager()
        username = tokenManager.verify_token(token)
        error = None
        if username is None:
            error = 'Invalid token. Please try again.'

        if error is not None:
            flash(error, 'error')
            return redirect(url_for('auth.login'))

        return render_template('resetPasswordForm.html', token=token)

    elif request.method == 'POST':
        password = request.form['password']
        tokenManager = TokenManager()
        username = tokenManager.verify_token(token)

        error = None
        if not password:
            error = 'Password is required.'

        if error is not None:
            flash(error, 'error')
            return render_template('resetPasswordForm.html', token=token)

        with DatabaseConnector(database=users_db) as connector:
            user_manager = UserManager(connector)
            # Change password
            user_manager.change_password(username, password)
            flash('Password changed successfully. Please login.', 'success')
            return redirect(url_for('auth.login'))
