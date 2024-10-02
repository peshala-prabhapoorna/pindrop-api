from typing import Annotated, Tuple

from fastapi import APIRouter, Depends, HTTPException, status

from src.dependencies import Database
from src.utils import utc_now
from src.users.dependencies import get_current_active_user
from src.users.schemas import UserInDB
from .schemas import ReportIn, ReportEdit, ReportInDB
from .dependencies import authorize_changes_to_report
from .utils import get_report_by_id, row_to_report, rows_to_reports


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
    report: ReportInDB = get_report_by_id(report_id, db)
    return report


@router.delete("/{report_id}")
async def delete_report(
    db: Annotated[Database, Depends(Database)],
    report: Annotated[ReportInDB, Depends(authorize_changes_to_report)],
):
    sql = (
        "UPDATE reports "
        "SET deleted_at = %s "
        "WHERE id = %s AND deleted_at IS NULL "
        "RETURNING title, deleted_at;"
    )
    values = (utc_now(), report.id)
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
    report_update: ReportEdit,
    db: Annotated[Database, Depends(Database)],
    report: Annotated[ReportInDB, Depends(authorize_changes_to_report)],
) -> ReportInDB:
    update_data = report_update.model_dump(exclude_unset=True)
    if update_data == {}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no new values to update",
        )

    report_in_db_model = ReportEdit(
        title=report.title,
        location=report.location,
        directions=report.directions,
        description=report.description,
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
        report.id,
    )
    db.cursor.execute(update_sql, update_values)
    updated_row = db.cursor.fetchone()
    db.connection.commit()

    response_report: ReportInDB = row_to_report(updated_row)

    return response_report
