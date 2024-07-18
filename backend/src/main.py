from fastapi import FastAPI
import sys

# add 'database' folder to the system path
sys.path.insert(0, "database")
import connect

from utilities import Report, reports_to_dict 

app = FastAPI()

# connect to PostgreSQL server
db_connection = connect.connect()
db_cursor = db_connection.cursor()


@app.get("/api/v0/")
async def root():
    return {"message": "returns something"}


@app.post("/api/v0/post/")
async def create_report(report: Report):
    sql = (
        "INSERT INTO reports(timestamp, title, location, directions, "
        "description, up_votes, down_votes)"
        "VALUES(%s, %s, %s, %s, %s, %s, %s)"
        "RETURNING *;"
    )

    values = (
        report.timestamp,
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

    return {
        "id": entry[0],
        "timestamp": entry[1],
        "title": entry[2],
        "location": entry[3],
        "directions": entry[4],
        "description": entry[5],
        "up_votes": entry[6],
        "down_votes": entry[7],
    }


@app.get("/api/v0/reports/")
async def get_all_posts():
    db_cursor.execute("SELECT * FROM reports;")
    rows = db_cursor.fetchall()

    return reports_to_dict(rows)
