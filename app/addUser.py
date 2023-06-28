from routes.db import DatabaseConnector, UserManager, ContactManager
from dotenv import load_dotenv
import os

load_dotenv()

username = 'newTestUser'
password = os.getenv('NEW_USER_PASSWORD')
email = 'newuser@gmail.com'

users_db = os.path.join(os.getenv('DB_PATH'), "users.db")

with DatabaseConnector(database=users_db) as connector:
    user_manager = UserManager(connector)
    user_manager.add_user(username, password, email, username + ".db")
