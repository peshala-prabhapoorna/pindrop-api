from typing import Tuple

from fastapi import HTTPException, status

from src.dependencies import Database
from .schemas import ReportInDB, ReportsInDB


def row_to_report(row) -> ReportInDB:
    report = ReportInDB(
        id=row[0],
        timestamp=row[1],
        user_id=row[2],
        title=row[3],
        location=row[4],
        directions=row[5],
        description=row[6],
    )

    return report


def rows_to_reports(rows):
    reports = []
    for row in rows:
        report = row_to_report(row)
        reports.append(report)

    return ReportsInDB(reports=reports)


def get_report_by_id(report_id: int, db: Database) -> ReportInDB:
    sql = "SELECT * FROM reports WHERE id=%s AND deleted_at IS NULL;"
    values = (report_id,)
    db.cursor.execute(sql, values)
    row: Tuple | None = db.cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report does not exist",
        )

    report: ReportInDB = row_to_report(row)
    return report
