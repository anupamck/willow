from flask import Blueprint, render_template
import mysql.connector
import os

home_bp = Blueprint('home', __name__)

config = {
    'user': 'u355617091_anupamck',
    'password': os.getenv('DB_PASSWORD'),
    'host': 'sql1017.main-hosting.eu',
    'database': 'u355617091_willow'
}


@home_bp.route('/')
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
                overdue_dict = {"id": contact[0], "name": contact[1],
                                "frequency": contact[2], "last_interaction": contact[3]}
                overdue_dicts.append(overdue_dict)
            return render_template('home.html', contacts=overdue_dicts)
