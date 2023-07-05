from routes.db import DatabaseConnector, UserManager, ContactManager
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

username = 'kalaikovan'
password = os.getenv('NEW_USER_PASSWORD')
email = 'kalai.march90@gmail.com'

users_db = os.path.join(os.getenv('DB_PATH'), "users.db")
db_path = os.path.join(os.getenv('DB_PATH'), username + '.db')

with DatabaseConnector(database=users_db) as connector:
    user_manager = UserManager(connector)
    user_manager.add_user(username, password, email, username + ".db")

conn = sqlite3.connect(db_path)
conn.close()
with DatabaseConnector(database=db_path) as connector:
    user_manager = UserManager(connector)
    user_manager.initialize_user_db()
