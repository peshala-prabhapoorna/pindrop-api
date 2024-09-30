from typing import Annotated, Tuple

from fastapi import APIRouter, Depends, HTTPException, status

from src.dependencies import Database
from src.utils import utc_now
from src.users.dependencies import get_current_active_user
from src.users.schemas import UserInDB
from .schemas import ReportIn, ReportEdit
from .utils import row_to_report, rows_to_reports


router = APIRouter(prefix="/api/v0/reports", tags=["reports"])


@router.post("")
async def create_report(
    report: ReportIn,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    sql = (
        "INSERT INTO reports(timestamp, user_id, title, location, "
        "directions, description, up_votes, down_votes)"
        "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        "RETURNING *;"
    )

    values = (
        utc_now(),
        current_user.id,
        report.title,
        report.location,
        report.directions,
        report.description,
        0,
        0,
    )

    db.cursor.execute(sql, values)
    row = db.cursor.fetchone()
    db.connection.commit()

    new_report = row_to_report(row)

    return new_report


@router.get("")
async def get_all_reports(db: Annotated[Database, Depends(Database)]):
    db.cursor.execute("SELECT * FROM reports WHERE deleted_at IS NULL;")
    rows = db.cursor.fetchall()

    return rows_to_reports(rows)


@router.get("/{report_id}")
async def get_one_report(
    report_id: int, db: Annotated[Database, Depends(Database)]
):
    sql = "SELECT * FROM reports WHERE id = %s AND deleted_at IS NULL;"
    db.cursor.execute(sql, (report_id,))
    row = db.cursor.fetchone()

    if row is None:
        return {"message": "report does not exist"}

    report = row_to_report(row)

    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    sql = "SELECT user_id FROM reports WHERE id=%s AND deleted_at IS NULL;"
    values = (report_id,)
    db.cursor.execute(sql, values)
    row: Tuple | None = db.cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report does not exist",
        )

    if current_user.id != row[0]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="report is not owned by the user",
        )

    sql = (
        "UPDATE reports "
        "SET deleted_at = %s "
        "WHERE id = %s AND deleted_at IS NULL "
        "RETURNING title, deleted_at;"
    )
    values = (utc_now(), report_id)
    db.cursor.execute(sql, values)
    row: Tuple | None = db.cursor.fetchone()
    db.connection.commit()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to delete report",
        )

    return {"message": "report deleted", "title": row[0], "deleted_at": row[1]}


@router.patch("/{report_id}")
async def edit_report(
    report_id: int,
    report: ReportEdit,
    db: Annotated[Database, Depends(Database)],
):
    update_data = report.model_dump(exclude_unset=True)
    if update_data == {}:
        return {"message": "no new values to update"}

    select_sql = (
        "SELECT title, location, directions, description "
        "FROM reports "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    db.cursor.execute(select_sql, (report_id,))
    row = db.cursor.fetchone()

    if row is None:
        return {"message": "report does not exist"}

    report_in_db_model = ReportEdit(
        title=row[0], location=row[1], directions=row[2], description=row[3]
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
        report_id,
    )
    db.cursor.execute(update_sql, update_values)
    updated_row = db.cursor.fetchone()
    db.connection.commit()

    report = row_to_report(updated_row)

    return report
