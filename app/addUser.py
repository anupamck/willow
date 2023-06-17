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
    'user': 'u936540649_willowProd',
            'password': os.getenv('TEST_USER_PASSWORD'),
            'host': 'srv976.hstgr.io',
            'database': 'u936540649_willowProd'
}

with DatabaseConnector(config=config_users_db) as connector:
    user_manager = UserManager(connector)
    user_manager.add_user('brahma', os.getenv(
        'CREATOR_PASSWORD'), 'wingfooted@gmail.com', config_test_user_db)
