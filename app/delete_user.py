from routes.db import DatabaseConnector, UserManager
from dotenv import load_dotenv
import os
import sqlite3
import sys

load_dotenv()


def delete_user(username, db='local'):
    if db == 'remote':
        db_folder = os.path.join(os.getenv('DB_PATH_REMOTE'))
    else:
        db_folder = os.path.join(os.getenv('DB_PATH'))
    users_db = os.path.join(db_folder, "users.db")
    db_path = os.path.join(db_folder, username + '.db')

    with DatabaseConnector(database=users_db) as connector:
        try:
            # Delete user from users table
            user_manager = UserManager(connector)
            user_manager.delete_user(username)

            # Delete user database file
            os.remove(db_path)
            print(f'User {username} deleted successfully')
        except sqlite3.Error as error:
            print(f'Error deleting user {username}: {error}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    if len(sys.argv) > 2:
        db = sys.argv[2]
    delete_user(username, db)
