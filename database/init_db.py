import os

import connect

# connect to the database
db_connection = connect.connect()
db_cursor = db_connection.cursor()

directory = "database/sql"

print("Initializing database...")

for file_path in os.listdir(directory):
    file_path = f"{directory}/{file_path}"
    with open(file_path, "r") as file:
        db_cursor.execute(file.read())

db_connection.commit()

print("Database initialization complete")

db_cursor.close()
db_connection.close()
