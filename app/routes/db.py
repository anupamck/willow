import sqlite3
import os
import bcrypt
import json
from cryptography.fernet import Fernet


class DatabaseConnector:
    def __init__(self, database=None):
        self.database = database
        self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        self.connection = sqlite3.connect(self.database)

    def close(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        with self.connection:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        return result


class ContactManager:
    def __init__(self, connector):
        self.connector = connector

    def get_overdue_contacts(self):
        query = '''SELECT c.id, c.name, c.frequency, MAX(i.date) AS last_interaction
                    FROM contacts c
                    LEFT JOIN interactions i ON i.person_id = c.id
                    GROUP BY c.id, c.name, c.frequency
                    HAVING (JULIANDAY('now') - JULIANDAY(MAX(i.date))) 
                    >= c.frequency AND c.frequency > 0
                    ORDER BY c.frequency ASC;'''
        with self.connector as cnx:
            return cnx.execute_query(query)

    def get_contacts(self):
        query = '''SELECT id, name, frequency FROM contacts ORDER BY name ASC'''
        with self.connector as cnx:
            return cnx.execute_query(query)

    def get_contact(self, person_id):
        query = '''SELECT id, name, frequency FROM contacts WHERE id = ?'''
        params = (person_id,)
        with self.connector as cnx:
            contact_array = cnx.execute_query(query, params)
            if len(contact_array) == 1:
                return contact_array[0]
            else:
                raise Exception('Contact not found')

    def add_contact(self, name, frequency):
        query = 'INSERT INTO contacts (name, frequency) VALUES (?, ?)'
        params = (name, frequency)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def edit_contact(self, person_id, name, frequency):
        query = 'UPDATE contacts SET name = ?, frequency = ? WHERE id = ?'
        params = (name, frequency, person_id)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def delete_contact(self, person_id):
        query = 'DELETE FROM contacts WHERE id = ?'
        params = (person_id,)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()


class InteractionManager:
    def __init__(self, connector):
        self.connector = connector

    def get_interactions(self, person_id):
        query = '''SELECT id, date, title, notes FROM interactions WHERE person_id = ? ORDER BY date DESC'''
        params = (person_id,)
        with self.connector as cnx:
            return cnx.execute_query(query, params)

    def get_interaction(self, interaction_id):
        query = '''SELECT id, date, title, notes FROM interactions WHERE id = ?'''
        params = (interaction_id,)
        with self.connector as cnx:
            interaction_array = cnx.execute_query(query, params)
            if len(interaction_array) == 1:
                return interaction_array[0]
            else:
                raise Exception('Interaction not found')

    def add_interaction(self, person_id, date, title, notes):
        query = 'INSERT INTO interactions (person_id, date, title, notes) VALUES (?, ?, ?, ?)'
        params = (person_id, date, title, notes)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def edit_interaction(self, interaction_id, date, title, notes):
        query = 'UPDATE interactions SET date = ?, title = ?, notes = ? WHERE id = ?'
        params = (date, title, notes, interaction_id)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def delete_interaction(self, interaction_id):
        query = 'DELETE FROM interactions WHERE id = ?'
        params = (interaction_id,)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()


class UserManager:
    def __init__(self, connector):
        self.connector = connector

    def add_user(self, username, password, email, database):
        salt = bcrypt.gensalt()
        password_enc = bcrypt.hashpw(password.encode('utf-8'), salt)
        query = 'INSERT INTO users (username, password, salt, email, database) VALUES (?, ?, ?, ?, ?)'
        params = (username, password_enc, salt, email, database)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()

    def initialize_user(self):
        query_interactions_table = '''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            person_id INTEGER,
            date DATE,
            title TEXT,
            notes TEXT
        );
        '''
        query_contacts_table = '''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            name TEXT,
            frequency INT
        );
        '''
        with self.connector as cnx:
            cnx.execute_query(query_interactions_table)
            cnx.execute_query(query_contacts_table)
            cnx.connection.commit()

    def delete_user(self, username):
        query = 'DELETE FROM users WHERE username = ?'
        params = (username,)
        with self.connector as cnx:
            cnx.execute_query(query, params)
            cnx.connection.commit()
        query = 'SELECT username FROM users'
        with self.connector as cnx:
            return cnx.execute_query(query)

    def get_user(self, username):
        query = 'SELECT * FROM users WHERE username = ?'
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
                    'database': os.path.join(os.getenv('DB_PATH'), user_details[5])
                }
            elif len(user_details_array) == 0:
                return None
            else:
                raise Exception(
                    'More than 1 user found with username ?', username)

    def is_password_correct(self, username, password):
        user = self.get_user(username)
        if user is None:
            return False
        else:
            password_enc = bcrypt.hashpw(
                password.encode('utf-8'), user['salt'].encode('utf-8'))
            return password_enc == user['password'].encode('utf-8')
