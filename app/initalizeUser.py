import os
from routes.db import DatabaseConnector, UserManager
from dotenv import load_dotenv

load_dotenv()


def initialize_user():
    username = 'chandragupta'
    password = os.getenv('TEST_USER_PASSWORD2')

    config = {
        'user': 'u936540649_' + username,
                'password': password,
                'host': 'srv976.hstgr.io',
                'database': 'u936540649_' + username
    }

    with DatabaseConnector(config=config) as connector:
        user_manager = UserManager(connector)
        user_manager.initialize_user()


if __name__ == '__main__':
    initialize_user()
