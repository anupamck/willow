from flask import Blueprint, render_template, request, flash
from ..routes.db import DatabaseConnector
import os

config = {
    'user': 'u936540649_anupamck',
            'password': os.getenv('DB_PASSWORD'),
            'host': 'srv976.hstgr.io',
            'database': 'u936540649_willow'
}

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def login_user():
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

        pass
