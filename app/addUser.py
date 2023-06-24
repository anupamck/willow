from routes.db import DatabaseConnector, UserManager, ContactManager
from dotenv import load_dotenv
import os

load_dotenv()

config_users_db = {
    'database': os.path.join(os.getenv('DB_PATH'), "users.db")
}

config_test_user_db = {
    'database': os.path.join(os.getenv('DB_PATH'), "new_test_user.db")
}

with DatabaseConnector(config=config_users_db) as connector:
    user_manager = UserManager(connector)
    user_manager.add_user('test_user', os.getenv(
        'TEST_USER_PASSWORD'), 'ashoka@magadha.com', config_test_user_db)
