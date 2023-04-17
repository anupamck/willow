import mysql.connector
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()

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
        with cnx.cursor() as cursor: # using a with block here opens a new connection ensures the cursor is closed when the block is exited
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

@app.route('/home')
def home():
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
                overdue_dict = {"id": contact[0], "name": contact[1], "frequency": contact[2], "last_interaction": contact[3]}
                overdue_dicts.append(overdue_dict)
            return render_template('home.html', contacts=overdue_dicts)

# Start server
if __name__ == '__main__':
    app.run(debug=True)
