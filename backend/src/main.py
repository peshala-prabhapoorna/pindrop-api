from fastapi import FastAPI
import sys

# add 'database' folder to the system path
sys.path.insert(0, "database")
import connect

from utilities import Report

app = FastAPI()

# connect to PostgreSQL server
db_connection = connect.connect()
db_cursor = db_connection.cursor()


@app.get("/api/v0/")
async def root():
    return {"message": "returns something"}


@app.post("/api/v0/post/")
async def create_post(report: Report):
    sql = (
        "INSERT INTO reports(date_time, title, location, directions, "
        "description, up_votes, down_votes)"
        "VALUES(%s, %s, %s, %s, %s, %s, %s)"
        "RETURNING *;"
    )

    values = (
        report.date_time,
        report.title,
        report.location,
        report.directions,
        report.description,
        report.up_votes,
        report.down_votes,
    )

    db_cursor.execute(sql, values)
    entry = db_cursor.fetchone()
    db_connection.commit()

    return entry
