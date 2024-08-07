from fastapi import FastAPI
import sys

# add 'database' folder to the system path
sys.path.insert(0, "database")
import connect

from utilities import (
    ReportIn,
    ReportEdit,
    row_to_report,
    rows_to_reports,
    utc_now,
)

app = FastAPI()

# connect to PostgreSQL server
db_connection = connect.connect()
db_cursor = db_connection.cursor()


@app.get("/api/v0")
async def root():
    return {"message": "this is pin-drop"}


@app.post("/api/v0/reports")
async def create_report(report: ReportIn):
    sql = (
        "INSERT INTO reports(timestamp, title, location, directions, "
        "description, up_votes, down_votes)"
        "VALUES(%s, %s, %s, %s, %s, %s, %s)"
        "RETURNING *;"
    )

    values = (
        utc_now(),
        report.title,
        report.location,
        report.directions,
        report.description,
        0,
        0,
    )

    db_cursor.execute(sql, values)
    row = db_cursor.fetchone()
    db_connection.commit()

    new_report = row_to_report(row)

    return new_report


@app.get("/api/v0/reports")
async def get_all_reports():
    db_cursor.execute("SELECT * FROM reports WHERE deleted_at IS NULL;")
    rows = db_cursor.fetchall()

    return rows_to_reports(rows)


@app.get("/api/v0/reports/{report_id}")
async def get_one_report(report_id):
    sql = "SELECT * FROM reports WHERE id = %s AND deleted_at IS NULL;"
    db_cursor.execute(sql, (report_id,))
    row = db_cursor.fetchone()

    if row is None:
        return {"message": "report does not exist"}

    report = row_to_report(row)

    return report


@app.delete("/api/v0/reports/{report_id}")
async def delete_report(report_id):
    sql = (
        "UPDATE reports "
        "SET deleted_at = %s "
        "WHERE id = %s AND deleted_at IS NULL "
        "RETURNING title, deleted_at;"
    )
    db_cursor.execute(sql, (utc_now(), report_id))
    row = db_cursor.fetchone()
    db_connection.commit()

    if row is None:
        return {"message": "report not deleted"}

    return {"message": "report deleted", "title": row[0], "deleted_at": row[1]}


@app.patch("/api/v0/reports/{report_id}")
async def edit_report(report_id: str, report: ReportEdit):
    update_data = report.model_dump(exclude_unset=True)
    if update_data == {}:
        return {"message": "no new values to update"}

    select_sql = (
        "SELECT title, location, directions, description "
        "FROM reports "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    db_cursor.execute(select_sql, (report_id,))
    row = db_cursor.fetchone()

    if row is None:
        return {"message": "report does not exist"}

    report_in_db_model = ReportEdit(
        title = row[0],
        location = row[1],
        directions = row[2],
        description = row[3]
    )

    updated_report_model = report_in_db_model.model_copy(update=update_data)
    update_sql = (
        "UPDATE reports "
        "SET title = %s, location = %s, directions = %s, description = %s "
        "WHERE id = %s "
        "RETURNING *;"
    )
    update_values = (
        updated_report_model.title,
        updated_report_model.location,
        updated_report_model.directions,
        updated_report_model.description,
        report_id
    )
    db_cursor.execute(update_sql, update_values)
    updated_row = db_cursor.fetchone()
    db_connection.commit()

    report = row_to_report(updated_row)

    return report
