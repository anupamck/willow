import os
from dotenv import load_dotenv
from routes.db import DatabaseConnector

load_dotenv()

database_folder = os.getenv('DB_PATH')

db_files = [f for f in os.listdir(database_folder) if f.endswith('.db')]

for db_file in db_files:
    db_path = os.path.join(database_folder, db_file)

    if db_file == 'users.db':
        continue

    with DatabaseConnector(database=db_path) as connector:
        query = 'ALTER TABLE contacts RENAME TO contacts_old;'
        with connector as cnx:
            cnx.execute_query(query)
            cnx.connection.commit()

        query = 'CREATE TABLE contacts (id INTEGER PRIMARY KEY, name TEXT, frequency INTEGER);'
        with connector as cnx:
            cnx.execute_query(query)
            cnx.connection.commit()

        query = 'INSERT INTO contacts (id, name, frequency) SELECT id, name, CAST(frequency AS INTEGER) FROM contacts_old;'
        with connector as cnx:
            cnx.execute_query(query)
            cnx.connection.commit()

        query = 'DROP TABLE contacts_old;'
        with connector as cnx:
            cnx.execute_query(query)
            cnx.connection.commit()
