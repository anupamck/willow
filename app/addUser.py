from routes.db import DatabaseConnector, UserManager, ContactManager
from dotenv import load_dotenv
import os

load_dotenv()

username = 'brahma'
password = os.getenv('USER_PASSWORD')
email = 'wingfooted@gmail.com'

users_db = os.path.join(os.getenv('DB_PATH'), "users.db")

with DatabaseConnector(database=users_db) as connector:
    user_manager = UserManager(connector)
    user_manager.add_user(username, password, email, username + ".db")
