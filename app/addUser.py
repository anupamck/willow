from routes.db import DatabaseConnector, UserManager, ContactManager
from dotenv import load_dotenv
import os

load_dotenv()

users_db = os.path.join(os.getenv('DB_PATH'), "users.db")

test_user_db = os.path.join(os.getenv('DB_PATH'), "new_test_user.db")

with DatabaseConnector(database=users_db) as connector:
    user_manager = UserManager(connector)
    user_manager.add_user('test_user', os.getenv(
        'TEST_USER_PASSWORD'), 'ashoka@magadha.com', test_user_db)
