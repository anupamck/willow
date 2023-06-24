from flask import Blueprint, render_template
from ..routes.db import DatabaseConnector, ContactManager, UserManager
from flask_login import login_required, current_user
from ..routes.auth import User
from cryptography.fernet import Fernet
import os


home_bp = Blueprint('home', __name__)


@home_bp.route('/home')
@login_required
def get_home():
    user = User.get(current_user.username)
    with DatabaseConnector(user.database) as connector:
        contact_manager = ContactManager(connector)
        overdue_contacts = contact_manager.get_overdue_contacts()
        overdue_dicts = []
        for contact in overdue_contacts:
            overdue_dict = {"id": contact[0], "name": contact[1],
                            "frequency": contact[2], "last_interaction": contact[3]}
            overdue_dicts.append(overdue_dict)
        return render_template('home.html', contacts=overdue_dicts)
