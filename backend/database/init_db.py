import os

import connect

# connect to the database
connection = connect.connect()
db_cursor = connection.cursor()

directory = "database/sql"

for file_path in os.listdir(directory):
    file_path = f"{directory}/{file_path}"
    with open(file_path, "r") as file:
        db_cursor.execute(file.read())
