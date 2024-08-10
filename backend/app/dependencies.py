import sys

# add 'database' folder to the system path
sys.path.insert(0, "database")
import connect


# connect to PostgreSQL server
db_connection = connect.connect()
db_cursor = db_connection.cursor()
