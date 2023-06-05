from flask import Blueprint, render_template
from ..routes.db import DB

home_bp = Blueprint('home', __name__)
db = DB()


@home_bp.route('/')
def get_home():
    overdue_contacts = db.get_overdue_contacts()
    # Convert the list of lists to a list of dictionaries
    overdue_dicts = []
    for contact in overdue_contacts:
        overdue_dict = {"id": contact[0], "name": contact[1],
                        "frequency": contact[2], "last_interaction": contact[3]}
        overdue_dicts.append(overdue_dict)
    return render_template('home.html', contacts=overdue_dicts)
