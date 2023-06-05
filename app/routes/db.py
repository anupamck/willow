import mysql.connector
import os


class DB:
    def __init__(self, config={
        'user': 'u355617091_anupamck',
        'password': os.getenv('DB_PASSWORD'),
        'host': 'sql1017.main-hosting.eu',
        'database': 'u355617091_willow'
    }):
        self.config = config

    def get_overdue_contacts(self):
        with mysql.connector.connect(**self.config) as cnx:
            with cnx.cursor() as cursor:
                cursor.execute('''SELECT c.id, c.name, c.frequency, max(i.date) as last_interaction
                                FROM contacts c
                                LEFT JOIN interactions i ON i.person_id = c.id
                                GROUP BY c.id, c.name, c.frequency
                                HAVING (DATEDIFF(NOW(), max(i.date))) 
                                >= c.frequency AND c.frequency > 0
                                ORDER BY c.frequency ASC;''')
                overdue_contacts = cursor.fetchall()
        return overdue_contacts

    def get_contacts(self):
        with mysql.connector.connect(**self.config) as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(
                    '''SELECT id, name, frequency FROM contacts ORDER BY name ASC''')
                contacts = cursor.fetchall()
        return contacts

    def get_contact(self, person_id):
        with mysql.connector.connect(**self.config) as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(
                    '''SELECT id, name, frequency FROM contacts WHERE id = %s''', (person_id,))
                contact = cursor.fetchone()
        return contact

    def add_contact(self, name, frequency):
        with mysql.connector.connect(**self.config) as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO contacts (name, frequency) VALUES (%s, %s)', (name, frequency))
                cnx.commit()

    def update_contact(self, person_id, name, frequency):
        with mysql.connector.connect(**self.config) as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(
                    'UPDATE contacts SET name = %s, frequency = %s WHERE id = %s', (name, frequency, person_id))
                cnx.commit()

    def delete_contact(self, person_id):
        with mysql.connector.connect(**self.config) as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(
                    'DELETE FROM contacts WHERE id = %s', (person_id,))
                cnx.commit()
