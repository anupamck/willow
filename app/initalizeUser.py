import os
from routes.db import DatabaseConnector, UserManager
from dotenv import load_dotenv
import sqlite3

load_dotenv()


def initialize_user_db():
    username = 'prerana'
    db_path = os.path.join(os.getenv('DB_PATH'), username + '.db')
    conn = sqlite3.connect(db_path)
    conn.close()

    with DatabaseConnector(database=db_path) as connector:
        user_manager = UserManager(connector)
        user_manager.initialize_user_db()


if __name__ == '__main__':
    initialize_user_db()
