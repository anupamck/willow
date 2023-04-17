import mysql.connector
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()

# Replace the variables below with your MySQL database credentials
config = {
    'user': 'u355617091_anupamck',
    'password': os.getenv('DB_PASSWORD'),
    'host': 'sql169.main-hosting.eu',
    'database': 'u355617091_willow'
}

# Create Flask app
app = Flask(__name__)
CORS(app)

# Create route to fetch contacts data
@app.route('/contacts')
def get_contacts():
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('SELECT id, name, frequency FROM contacts ORDER BY name ASC')
            contacts = cursor.fetchall()

            # Convert the list of lists to a list of dictionaries
            contact_dicts = []
            for contact in contacts:
                contact_dict = {"id": contact[0], "name": contact[1], "frequency": contact[2]}
                contact_dicts.append(contact_dict)
        return render_template('contacts.html', contacts=contact_dicts)

# Create route to fetch interactions data
@app.route('/interactions/<int:person_id>/<string:contact_name>')
def interactions(person_id, contact_name):
    with mysql.connector.connect(**config) as cnx:
        with cnx.cursor() as cursor:
            cursor.execute('SELECT * FROM interactions WHERE person_id = %s', (person_id,))
            interactions = cursor.fetchall()

            # Convert the list of lists to a list of dictionaries
            interaction_dicts = []
            for interaction in interactions:
                interaction_dict = {"date": interaction[2], "title": interaction[3], "notes": interaction[4]}
                interaction_dicts.append(interaction_dict)
        return render_template('interactions.html', interactions=interaction_dicts, contact_name=contact_name)

# Start server
if __name__ == '__main__':
    app.run(debug=True)
