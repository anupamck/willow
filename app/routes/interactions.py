from flask import Blueprint, render_template, redirect, url_for, request
import mysql.connector
import os
from flask import request, flash


interactions_bp = Blueprint('interactions', __name__)

config = {
    'user': 'u355617091_anupamck',
    'password': os.getenv('DB_PASSWORD'),
    'host': 'sql1017.main-hosting.eu',
    'database': 'u355617091_willow'
}


@interactions_bp.route('/interactions/<int:person_id>/<string:contact_name>')
def get_interactions(person_id, contact_name):
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM interactions WHERE person_id = %s ORDER BY date DESC', (person_id,))
            interactions = cursor.fetchall()

            # Convert the list of lists to a list of dictionaries
            interaction_dicts = []
            for interaction in interactions:
                interaction_dict = {
                    "id": interaction[0], "date": interaction[2], "title": interaction[3], "notes": interaction[4]}
                interaction_dicts.append(interaction_dict)
        return render_template('interactions.html', interactions=interaction_dicts, contact_name=contact_name, person_id=person_id)


@interactions_bp.route('/add_interaction/<int:person_id>/<string:contact_name>', methods=['POST', 'GET'])
def add_interaction(person_id, contact_name):
    if request.method == 'GET':
        return render_template('interactionForm.html', person_id=person_id, contact_name=contact_name, form_type='add')

    elif request.method == 'POST':
        # Get the form data
        date = request.form['date']
        title = request.form['title']
        notes = request.form['notes']
        person_id = request.form['person_id']
        contact_name = request.form['contact_name']
        error = None

        if not date:
            error = 'Date is required.'
        if not title or not notes:
            error = 'Title and notes are required.'

        if error is not None:
            flash(error)
            return render_template('interactionForm.html', person_id=person_id, contact_name=contact_name, form_type='add')

        else:
            # Add the interaction to the database
            with mysql.connector.connect(**config) as cnx:
                with cnx.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO interactions (person_id, date, title, notes) VALUES (%s, %s, %s, %s)', (person_id, date, title, notes))
                    cnx.commit()

            return redirect(url_for('interactions.get_interactions', person_id=person_id, contact_name=contact_name))


@interactions_bp.route('/update_interaction/<int:interaction_id>/<int:person_id>/<string:contact_name>', methods=['POST', 'GET'])
def update_interaction(interaction_id, person_id, contact_name):
    # Fetch interaction info from database to prefill edit form
    if request.method == 'GET':
        with mysql.connector.connect(**config) as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(
                    'SELECT * FROM interactions WHERE id = %s', (interaction_id,))
                interaction = cursor.fetchone()
        return render_template('interactionForm.html', interaction=interaction, person_id=person_id, contact_name=contact_name, form_type='edit')

    elif request.method == 'POST':
        # Get the form data
        interaction_id = request.form['id']
        date = request.form['date']
        title = request.form['title']
        notes = request.form['notes']
        person_id = request.form['person_id']
        contact_name = request.form['contact_name']

    # Update the interaction in the database
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute(
                'UPDATE interactions SET date = %s, title = %s, notes = %s WHERE id = %s', (date, title, notes, interaction_id))
            cnx.commit()

    return redirect(url_for('interactions.get_interactions', person_id=person_id, contact_name=contact_name))


@interactions_bp.route('/delete_interaction/<int:interaction_id>/<int:person_id>/<string:contact_name>')
def delete_interaction(interaction_id, person_id, contact_name):
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute(
                'DELETE FROM interactions WHERE id = %s', (interaction_id,))
            cnx.commit()
    return redirect(url_for('interactions.get_interactions', person_id=person_id, contact_name=contact_name))
