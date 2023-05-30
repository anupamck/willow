from flask import Blueprint, render_template, redirect, url_for, request
import mysql.connector
import os
from flask import request


contacts_bp = Blueprint('contacts', __name__)

config = {
    'user': 'u355617091_anupamck',
    'password': os.getenv('DB_PASSWORD'),
    'host': 'sql1017.main-hosting.eu',
    'database': 'u355617091_willow'
}


@contacts_bp.route('/contacts')
def get_contacts():
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:  # using a with block here opens a new connection ensures the cursor is closed when the block is exited
            cursor.execute(
                'SELECT id, name, frequency FROM contacts ORDER BY name ASC')
            contacts = cursor.fetchall()

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

    # Get the form data
    name = request.form['name']
    frequency = request.form['frequency']

    # Add the contact to the database
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute(
                'INSERT INTO contacts (name, frequency) VALUES (%s, %s)', (name, frequency))
            cnx.commit()

    # Redirect the user back to the contacts page
    return redirect(url_for('contacts.get_contacts'))


@contacts_bp.route('/update_contact/<int:person_id>', methods=['POST', 'GET'])
def update_contact(person_id):
    if request.method == 'GET':
        # Get the contact from the database to prefill edit form
        with mysql.connector.connect(**config) as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(
                    'SELECT * FROM contacts WHERE id = %s', (person_id,))
                contact = cursor.fetchone()

        # Render the form
        return render_template('contactForm.html', contact=contact, form_type='edit')

    elif request.method == 'POST':
        # Get the form data
        name = request.form['name']
        frequency = request.form['frequency']

    # Update the contact in the database
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute(
                'UPDATE contacts SET name = %s, frequency = %s WHERE id = %s', (name, frequency, person_id))
            cnx.commit()

    # Redirect the user back to the contacts page
    return redirect(url_for('contacts.get_contacts'))


@contacts_bp.route('/delete_contact/<int:person_id>')
def delete_contact(person_id):
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('DELETE FROM contacts WHERE id = %s', (person_id,))
            cnx.commit()
    return redirect(url_for('contacts.get_contacts'))
