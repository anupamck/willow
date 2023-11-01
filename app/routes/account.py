from flask import Blueprint, request, render_template, redirect, url_for, flash
from ..routes.db import DatabaseConnector, UserManager
from flask_login import login_required, current_user, logout_user
from ..routes.auth import User
import os

account_bp = Blueprint('account', __name__)

users_db = os.path.join(os.getenv('DB_PATH'), "users.db")


@account_bp.route('/account')
@login_required
def get_account_details():

    return render_template('account.html')


@account_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():

    if request.method == 'GET':
        return render_template('changePasswordForm.html')

    elif request.method == 'POST':
        # Get the form data
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        error = None
        if not current_password:
            error = 'Current password is required.'
        elif not new_password:
            error = 'New password is required.'
        elif not confirm_password:
            error = 'Confirm new password is required.'
        elif new_password != confirm_password:
            error = 'New password and confirm new password must match.'

        if error is not None:
            flash(error, 'error')
            return render_template('changePasswordForm.html')

        else:
            with DatabaseConnector(database=users_db) as connector:
                user_manager = UserManager(connector)
                if user_manager.is_password_correct(current_user.username, current_password):
                    user_manager.change_password(
                        current_user.username, new_password)
                    flash('Password changed successfully.', 'success')
                    return redirect(url_for('account.get_account_details'))
                else:
                    error = 'Current password is incorrect.'
                    flash(error, 'error')
                    return render_template('changePasswordForm.html')


@account_bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    if request.method == 'POST':
        with DatabaseConnector(database=users_db) as connector:
            # Delete user from users table
            user_manager = UserManager(connector)
            user_manager.delete_user(current_user.username)

            # Delete user database file
            db_path = os.path.join(os.getenv('DB_PATH'),
                                   current_user.username + '.db')
            os.remove(db_path)

            flash('Account deleted successfully.', 'success')
            logout_user()
            return redirect(url_for('auth.login'))


# Outgoing server: smtp.titan.email

# Port: 465

# Encryption method: SSL/TLS
