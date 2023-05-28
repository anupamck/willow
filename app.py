import mysql.connector
from flask import Flask, render_template, redirect, url_for, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()

config = {
    'user': 'u355617091_anupamck',
    'password': os.getenv('DB_PASSWORD'),
    'host': 'sql1017.main-hosting.eu',
    'database': 'u355617091_willow'
}

# Create Flask app
app = Flask(__name__)
CORS(app)

# Create route to fetch contacts data
@app.route('/contacts')
def get_contacts():
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor: # using a with block here opens a new connection ensures the cursor is closed when the block is exited
            cursor.execute('SELECT id, name, frequency FROM contacts ORDER BY name ASC')
            contacts = cursor.fetchall()

            # Convert the list of lists to a list of dictionaries
            contact_dicts = []
            for contact in contacts:
                contact_dict = {"id": contact[0], "name": contact[1].replace("'", "&#39;").replace('"', "&#34;").replace("\n", ""), "frequency": contact[2]}
                contact_dicts.append(contact_dict)
        return render_template('contacts.html', contacts=contact_dicts)

# Create route to fetch interactions data
@app.route('/interactions/<int:person_id>/<string:contact_name>')
def get_interactions(person_id, contact_name):
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('SELECT * FROM interactions WHERE person_id = %s ORDER BY date DESC', (person_id,))
            interactions = cursor.fetchall()

            # Convert the list of lists to a list of dictionaries
            interaction_dicts = []
            for interaction in interactions:
                interaction_dict = {"id": interaction[0], "date": interaction[2], "title": interaction[3].replace("'", "&#39;").replace('"', "&#34;").replace("\n", ""), "notes": interaction[4].replace("'", "&#39;").replace('"', "&#34;").replace("\n", "&#10;")}
                interaction_dicts.append(interaction_dict)
        return render_template('interactions.html', interactions=interaction_dicts, contact_name=contact_name.replace("'", "&#39;").replace('"', "&#34;").replace("\n", ""), person_id=person_id)

@app.route('/home')
def get_home():
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('''SELECT c.id, c.name, c.frequency, max(i.date) as last_interaction
                            FROM contacts c
                            LEFT JOIN interactions i ON i.person_id = c.id
                            GROUP BY c.id, c.name, c.frequency
                            HAVING (DATEDIFF(NOW(), max(i.date))) 
                            >= c.frequency AND c.frequency > 0
                            ORDER BY c.frequency ASC;''')
            overdue_contacts = cursor.fetchall()

            # Convert the list of lists to a list of dictionaries
            overdue_dicts = []
            for contact in overdue_contacts:
                overdue_dict = {"id": contact[0], "name": contact[1].replace("'", "&#39;").replace('"', "&#34;").replace("\n", ""), "frequency": contact[2], "last_interaction": contact[3]}
                overdue_dicts.append(overdue_dict)
            return render_template('home.html', contacts=overdue_dicts)
        
@app.route('/delete_contact/<int:person_id>')
def delete_contact(person_id):
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('DELETE FROM contacts WHERE id = %s', (person_id,))
            cnx.commit()
    return redirect(url_for('get_contacts'))

@app.route('/delete_interaction/<int:interaction_id>/<int:person_id>/<string:contact_name>')
def delete_interaction(interaction_id, person_id, contact_name):
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('DELETE FROM interactions WHERE id = %s', (interaction_id,))
            cnx.commit()
    return redirect(url_for ('get_interactions', person_id=person_id, contact_name=contact_name))

from flask import request

@app.route('/update_contact/<int:person_id>', methods=['POST', 'GET'])
def update_contact(person_id):
    if request.method == 'GET':
        # Fetch contact info from database to prefil edit form
        with mysql.connector.connect(**config) as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute('SELECT * FROM contacts WHERE id = %s', (person_id,))
            contact = cursor.fetchone()
        return render_template('contactForm.html', contact=contact, form_type='edit')
    
    elif request.method == 'POST':
      # Get the form data
        name = request.form['name']
        frequency = request.form['frequency']

    # Update the contact in the database
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('UPDATE contacts SET name = %s, frequency = %s WHERE id = %s', (name, frequency, person_id))
            cnx.commit()

    # Redirect the user back to the contacts page
    return redirect(url_for('get_contacts'))

@app.route('/update_interaction', methods=['POST'])
def update_interaction():
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
            cursor.execute('UPDATE interactions SET date = %s, title = %s, notes = %s WHERE id = %s', (date, title, notes, interaction_id))
            cnx.commit()

    # Redirect the user back to the interactions page
    return redirect(url_for('get_interactions', person_id=person_id, contact_name=contact_name))

@app.route('/add_contact', methods=['POST', 'GET'])
def add_contact():
    if request.method == 'GET':
        return render_template('contactForm.html', form_type='add')

    # Get the form data
    name = request.form['name']
    frequency = request.form['frequency']

    # Add the contact to the database
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('INSERT INTO contacts (name, frequency) VALUES (%s, %s)', (name, frequency))
            cnx.commit()

    # Redirect the user back to the contacts page
    return redirect(url_for('get_contacts'))

@app.route('/add_interaction', methods=['POST'])
def add_interaction():
    # Get the form data
    date = request.form['date']
    title = request.form['title']
    notes = request.form['notes']
    person_id = request.form['person_id']
    contact_name = request.form['contact_name']

    # Add the interaction to the database
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('INSERT INTO interactions (person_id, date, title, notes) VALUES (%s, %s, %s, %s)', (person_id, date, title, notes))
            cnx.commit()

    # Redirect the user back to the interactions page
    return redirect(url_for('get_interactions', person_id=person_id, contact_name=contact_name))


# Start server
if __name__ == '__main__':
    app.run(debug=True)
