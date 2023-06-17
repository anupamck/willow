from routes.db import DatabaseConnector, UserManager, ContactManager
from dotenv import load_dotenv
import os

load_dotenv()

config_users_db = {
    'user': 'u936540649_willowUsers',
            'password': os.getenv('USER_DB_PASSWORD'),
            'host': 'srv976.hstgr.io',
            'database': 'u936540649_willowUsers'
}

config_test_user_db = {
    'user': 'u936540649_willowTest',
            'host': 'srv976.hstgr.io',
            'database': 'u936540649_willowTest'
}

with DatabaseConnector(config=config_users_db) as connector:
    user_manager = UserManager(connector)
    user_manager.add_user('ashoka', os.getenv(
        'TEST_USER_PASSWORD'), 'ashoka@maghada.com', config_test_user_db)
