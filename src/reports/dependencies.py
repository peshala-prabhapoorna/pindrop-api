from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.dependencies import Database
from src.users.schemas import UserInDB
from src.users.dependencies import get_current_active_user
from .schemas import ReportInDB
from .queries import get_report_by_id


async def authorize_changes_to_report(
    report_id: int,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> ReportInDB:
    """
    Checks whether the current active user is authorized to make changes
    to the report to be edited.

    Parameters:
    `report_id`: id number of the report to be edited

    Dependencies:
    db           (Database): injects object with database access
    current_user (UserInDB): authenticates the current active user and
    injects its db record

    Returns:
    ReportInDB: current record of the report in `reports` table
    """

    report: ReportInDB = get_report_by_id(report_id, db)
    if current_user.id != report.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="report is not owned by the user",
        )

    return report
