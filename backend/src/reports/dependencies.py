from typing import Annotated, Tuple

from fastapi import Depends, HTTPException, status

from src.dependencies import Database
from src.users.schemas import UserInDB
from src.users.dependencies import get_current_active_user
from .schemas import ReportInDB
from .utils import row_to_report


async def authorize_changes_to_report(
    report_id: int,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> ReportInDB:
    sql = "SELECT * " "FROM reports " "WHERE id=%s AND deleted_at IS NULL;"
    values = (report_id,)
    db.cursor.execute(sql, values)
    row: Tuple | None = db.cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report does not exist",
        )

    report = row_to_report(row)
    if current_user.id != report.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="report is not owned by the user",
        )

    return report
