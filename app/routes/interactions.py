from flask import Blueprint, request, flash, render_template, redirect, url_for, request
from ..routes.db import DatabaseConnector, InteractionManager
from flask_login import login_required, current_user
from ..routes.auth import User
import datetime

interactions_bp = Blueprint('interactions', __name__)


@interactions_bp.route('/interactions/<int:person_id>/<string:contact_name>')
@login_required
def get_interactions(person_id, contact_name):
    user = User.get(current_user.username)
    with DatabaseConnector(database=user.database) as connector:
        interaction_manager = InteractionManager(connector)
        interactions = interaction_manager.get_interactions(person_id)
    # Convert the list of lists to a list of dictionaries
    interaction_dicts = []
    for interaction in interactions:
        interaction_dict = {
            "id": interaction[0], "date": interaction[1], "title": interaction[2], "notes": interaction[3]}
        interaction_dicts.append(interaction_dict)
    return render_template('interactions.html', interactions=interaction_dicts, contact_name=contact_name, person_id=person_id)


@interactions_bp.route('/add_interaction/<int:person_id>/<string:contact_name>', methods=['POST', 'GET'])
@login_required
def add_interaction(person_id, contact_name):
    # Format today's date as 'YYYY-MM-DD'
    today = datetime.date.today().strftime("%Y-%m-%d")
    if request.method == 'GET':
        return render_template('interactionForm.html', today=today, person_id=person_id, contact_name=contact_name, form_type='add')

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
            flash(error, 'error')
            return render_template('interactionForm.html', person_id=person_id, contact_name=contact_name, form_type='add')

        else:
            user = User.get(current_user.username)
            # Add the interaction to the database
            with DatabaseConnector(user.database) as connector:
                interaction_manager = InteractionManager(connector)
                interaction_manager.add_interaction(
                    person_id, date, title, notes)
            return redirect(url_for('interactions.get_interactions', person_id=person_id, contact_name=contact_name))


@interactions_bp.route('/edit_interaction/<int:interaction_id>/<int:person_id>/<string:contact_name>', methods=['POST', 'GET'])
@login_required
def edit_interaction(interaction_id, person_id, contact_name):
    user = User.get(current_user.username)
    # Fetch interaction info from database to prefill edit form
    if request.method == 'GET':
        with DatabaseConnector(user.database) as connector:
            interaction_manager = InteractionManager(connector)
            interaction = interaction_manager.get_interaction(interaction_id)
        return render_template('interactionForm.html', interaction=interaction, contact_name=contact_name, person_id=person_id, form_type='edit')

    elif request.method == 'POST':
        # Get the form data
        interaction_id = request.form['id']
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
            flash(error, 'error')
            with DatabaseConnector(user.database) as connector:
                interaction_manager = InteractionManager(connector)
                interaction = interaction_manager.get_interaction(
                    interaction_id)
                return render_template('interactionForm.html', interaction=interaction, contact_name=contact_name, person_id=person_id, form_type='edit')

    # Update the interaction in the database
    with DatabaseConnector(user.database) as connector:
        interaction_manager = InteractionManager(connector)
        interaction_manager.edit_interaction(
            interaction_id, date, title, notes)
    return redirect(url_for('interactions.get_interactions', person_id=person_id, contact_name=contact_name))


@interactions_bp.route('/delete_interaction/<int:interaction_id>/<int:person_id>/<string:contact_name>')
@login_required
def delete_interaction(interaction_id, person_id, contact_name):
    user = User.get(current_user.username)
    with DatabaseConnector(user.database) as connector:
        interaction_manager = InteractionManager(connector)
        interaction_manager.delete_interaction(interaction_id)
    return redirect(url_for('interactions.get_interactions', person_id=person_id, contact_name=contact_name))
