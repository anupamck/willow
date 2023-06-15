import mysql.connector
import os
import bcrypt
import json


class DatabaseConnector:
    def __init__(self, config=None):
        self.config = config or {
            'user': 'u936540649_willowTest',
            'password': os.getenv('DB_PASSWORD'),
            'host': 'srv976.hstgr.io',
            'database': 'u936540649_willowTest'
        }
        self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        self.connection = mysql.connector.connect(**self.config)

    def close(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        return result


class ContactManager:
    def __init__(self, connector):
        self.connector = connector

    def get_overdue_contacts(self):
        query = '''SELECT c.id, c.name, c.frequency, max(i.date) as last_interaction
                    FROM contacts c
                    LEFT JOIN interactions i ON i.person_id = c.id
                    GROUP BY c.id, c.name, c.frequency
                    HAVING (DATEDIFF(NOW(), max(i.date))) 
                    >= c.frequency AND c.frequency > 0
                    ORDER BY c.frequency ASC;'''
        with self.connector as cnx:
            return cnx.execute_query(query)

    def get_contacts(self):
        query = '''SELECT id, name, frequency FROM contacts ORDER BY name ASC'''
        with self.connector as cnx:
            return cnx.execute_query(query)

    def get_contact(self, person_id):
        query = '''SELECT id, name, frequency FROM contacts WHERE id = %s'''
        params = (person_id,)
        with self.connector as cnx:
            contact_array = cnx.execute_query(query, params)
            if len(contact_array) == 1:
                return contact_array[0]
            else:
                raise Exception('Contact not found')

    def add_contact(self, name, frequency):
        query = 'INSERT INTO contacts (name, frequency) VALUES (%s, %s)'
        params = (name, frequency)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def edit_contact(self, person_id, name, frequency):
        query = 'UPDATE contacts SET name = %s, frequency = %s WHERE id = %s'
        params = (name, frequency, person_id)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def delete_contact(self, person_id):
        query = 'DELETE FROM contacts WHERE id = %s'
        params = (person_id,)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()


class InteractionManager:
    def __init__(self, connector):
        self.connector = connector

    def get_interactions(self, person_id):
        query = '''SELECT id, date, title, notes FROM interactions WHERE person_id = %s ORDER BY date DESC'''
        params = (person_id,)
        with self.connector as cnx:
            return cnx.execute_query(query, params)

    def get_interaction(self, interaction_id):
        query = '''SELECT id, date, title, notes FROM interactions WHERE id = %s'''
        params = (interaction_id,)
        with self.connector as cnx:
            interaction_array = cnx.execute_query(query, params)
            if len(interaction_array) == 1:
                return interaction_array[0]
            else:
                raise Exception('Interaction not found')

    def add_interaction(self, person_id, date, title, notes):
        query = 'INSERT INTO interactions (person_id, date, title, notes) VALUES (%s, %s, %s, %s)'
        params = (person_id, date, title, notes)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def edit_interaction(self, interaction_id, date, title, notes):
        query = 'UPDATE interactions SET date = %s, title = %s, notes = %s WHERE id = %s'
        params = (date, title, notes, interaction_id)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def delete_interaction(self, interaction_id):
        query = 'DELETE FROM interactions WHERE id = %s'
        params = (interaction_id,)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()


class UserManager:
    def __init__(self, connector):
        self.connector = connector

    def add_user(self, username, password, email, dbConfig):
        salt = bcrypt.gensalt()
        password_enc = bcrypt.hashpw(password.encode('utf-8'), salt)
        dbPasword_enc = bcrypt.hashpw(
            dbConfig['password'].encode('utf-8'), salt)
        dbConfig['password'] = dbPasword_enc.decode('utf-8')
        dbConfig = json.dumps(dbConfig)
        query = 'INSERT INTO users (username, password, salt, email, config) VALUES (%s, %s, %s, %s, %s)'
        params = (username, password_enc, salt, email, dbConfig)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def delete_user(self, username):
        query = 'DELETE FROM users WHERE username = %s'
        params = (username,)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def get_users(self):
        query = 'SELECT username FROM users'
        with self.connector as cnx:
            return cnx.execute_query(query)

    def get_user(self, username):
        query = 'SELECT * FROM users WHERE username = %s'
        params = (username,)
        with self.connector as cnx:
            user_details_array = cnx.execute_query(query, params)
            if len(user_details_array) == 1:
                user_details = user_details_array[0]
                return {
                    'username': user_details[1],
                    'password': user_details[2],
                    'salt': user_details[3],
                    'email': user_details[4],
                    'config': json.loads(user_details[5])
                }
            elif len(user_details_array) == 0:
                return None
            else:
                raise Exception(
                    'More than 1 user found with username %s', username)

    def is_password_correct(self, username, password):
        user = self.get_user(username)
        if user is None:
            return False
        else:
            password_enc = bcrypt.hashpw(
                password.encode('utf-8'), user['salt'].encode('utf-8'))
            return password_enc == user['password'].encode('utf-8')
