from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask import request
from ..routes.db import DB


contacts_bp = Blueprint('contacts', __name__)
db = DB()


@contacts_bp.route('/contacts')
def get_contacts():
    contacts = db.get_contacts()
    # Convert the list of lists to a list of dictionaries
    contact_dicts = []
    for contact in contacts:
        contact_dict = {
            "id": contact[0], "name": contact[1], "frequency": contact[2]}
        contact_dicts.append(contact_dict)
    return render_template('contacts.html', contacts=contact_dicts)


@contacts_bp.route('/add_contact', methods=['POST', 'GET'])
def add_contact():
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
            flash(error)
            return render_template('contactForm.html', form_type='add')

        else:
            db.add_contact(name, frequency)
            # Redirect the user back to the contacts page
            return redirect(url_for('contacts.get_contacts'))


@contacts_bp.route('/update_contact/<int:person_id>', methods=['POST', 'GET'])
def update_contact(person_id):
    if request.method == 'GET':
        contact = db.get_contact(person_id)
        # Render the form
        return render_template('contactForm.html', contact=contact, form_type='edit')

    elif request.method == 'POST':
        # Get the form data
        name = request.form['name']
        frequency = request.form['frequency']
        db.update_contact(person_id, name, frequency)
        # Redirect the user back to the contacts page
        return redirect(url_for('contacts.get_contacts'))


@contacts_bp.route('/delete_contact/<int:person_id>')
def delete_contact(person_id):
    db.delete_contact(person_id)
    return redirect(url_for('contacts.get_contacts'))
