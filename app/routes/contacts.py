from flask import Blueprint, request, render_template, redirect, url_for, request, flash, make_response
from ..routes.db import DatabaseConnector, ContactManager
from flask_login import login_required, current_user
from ..routes.auth import User


contacts_bp = Blueprint('contacts', __name__)


@contacts_bp.route('/contacts')
@login_required
def get_contacts():
    user = User.get(current_user.username)
    with DatabaseConnector(database=user.database) as connector:
        contact_manager = ContactManager(connector)
        contacts = contact_manager.get_contacts()
        contact_dicts = []
        for contact in contacts:
            contact_dict = {"id": contact[0], "name": contact[1],
                            "frequency": contact[2]}
            contact_dicts.append(contact_dict)
    return render_template('contacts.html', contacts=contact_dicts)


@contacts_bp.route('/add_contact', methods=['POST', 'GET'])
@login_required
def add_contact():
    user = User.get(current_user.username)
    if request.method == 'GET':
        return render_template('contactForm.html', form_type='add')

    elif request.method == 'POST':
        # Get the form data
        name = request.form['name']
        frequency = request.form['frequency']
        error = None

        if not name:
            error = 'Name is required.'
        if not frequency:
            error = 'Frequency is required.'

        if error is not None:
            flash(error, 'error')
            return render_template('contactForm.html', form_type='add')

        else:
            with DatabaseConnector(user.database) as connector:
                contact_manager = ContactManager(connector)
                contact_manager.add_contact(name, frequency)
            # Redirect the user back to the contacts page
            return redirect(url_for('contacts.get_contacts'))


@contacts_bp.route('/edit_contact/<int:person_id>', methods=['POST', 'GET'])
@login_required
def edit_contact(person_id):
    user = User.get(current_user.username)
    if request.method == 'GET':
        with DatabaseConnector(user.database) as connector:
            contact_manager = ContactManager(connector)
            contact = contact_manager.get_contact(person_id)
        # Render the form
        return render_template('contactForm.html', contact=contact, form_type='edit')

    elif request.method == 'POST':
        # Get the form data
        name = request.form['name']
        frequency = request.form['frequency']
        error = None

        if not name:
            error = 'Name is required.'
        if not frequency:
            error = 'Frequency is required.'

        if error is not None:
            flash(error, 'error')
            with DatabaseConnector(user.database) as connector:
                contact_manager = ContactManager(connector)
                contact = contact_manager.get_contact(person_id)
                return render_template('contactForm.html', contact=contact, form_type='edit')

        with DatabaseConnector(user.database) as connector:
            contact_manager = ContactManager(connector)
            contact_manager.edit_contact(person_id, name, frequency)
        # Redirect the user back to the contacts page
        return redirect(url_for('contacts.get_contacts'))


@contacts_bp.route('/delete_contact/<int:person_id>')
@login_required
def delete_contact(person_id):
    user = User.get(current_user.username)
    with DatabaseConnector(user.database) as connector:
        contact_manager = ContactManager(connector)
        contact_manager.delete_contact(person_id)
    return redirect(url_for('contacts.get_contacts'))
