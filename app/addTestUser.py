from routes.db import DatabaseConnector, UserManager, ContactManager
from dotenv import load_dotenv
import os

load_dotenv()

config = {
    'user': 'u936540649_willowUsers',
            'password': os.getenv('USER_DB_PASSWORD'),
            'host': 'srv976.hstgr.io',
            'database': 'u936540649_willowUsers'
}

with DatabaseConnector(config=config) as connector:
    user_manager = UserManager(connector)
    user_manager.add_user('ashoka', os.getenv('TEST_USER_PASSWORD'))
