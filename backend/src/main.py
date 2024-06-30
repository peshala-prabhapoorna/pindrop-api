from fastapi import FastAPI
import sys

# add 'database' folder to the system path
sys.path.insert(0, "database")
import connect

app = FastAPI()

# connect to PostgreSQL server
db_connection = connect.connect()
db_cursor = db_connection.cursor()
db_cursor.execute("SELECT version();")
db_version = db_cursor.fetchone()
print(db_version)

@app.get("/api/v0/")
async def root():
    return {"message": "returns something"}
