from typing import Annotated, Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, status

from src.dependencies import Database
from src.utils import utc_now
from src.users.dependencies import get_current_active_user
from src.users.schemas import UserInDB
from .schemas import (
    ReportIn,
    ReportEdit,
    ReportInDB,
    ReportStatEdit,
    ReportStatInDB,
    ReportsInDB,
    VoteEdit,
    VoteInDB,
)
from .dependencies import authorize_changes_to_report
from .utils import row_to_report, rows_to_reports
from .queries import (
    get_previous_vote,
    get_report_by_id,
    get_report_stats,
    record_vote,
    update_report_stats,
)

router = APIRouter(prefix="/api/v0/reports", tags=["reports"])


@router.post("")
async def create_report(
    report: ReportIn,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> ReportInDB:
    # create report
    sql = (
        "INSERT INTO reports(timestamp, user_id, title, location, "
        "directions, description)"
        "VALUES(%s, %s, %s, %s, %s, %s)"
        "RETURNING *;"
    )
    values = (
        utc_now(),
        current_user.id,
        report.title,
        report.location,
        report.directions,
        report.description,
    )
    db.cursor.execute(sql, values)
    row = db.cursor.fetchone()

    new_report: ReportInDB = row_to_report(row)

    # report_stats record
    sql = "INSERT INTO report_stats(report_id) VALUES (%s);"
    values = (new_report.id,)
    db.cursor.execute(sql, values)
    db.connection.commit()

    return new_report


@router.get("")
async def get_all_reports(
    db: Annotated[Database, Depends(Database)],
) -> ReportsInDB:
    db.cursor.execute("SELECT * FROM reports WHERE deleted_at IS NULL;")
    rows = db.cursor.fetchall()

    return rows_to_reports(rows)


@router.get("/{report_id}")
async def get_one_report(
    report_id: int, db: Annotated[Database, Depends(Database)]
) -> ReportInDB:
    report: ReportInDB = get_report_by_id(report_id, db)
    return report


@router.delete("/{report_id}")
async def delete_report(
    db: Annotated[Database, Depends(Database)],
    report: Annotated[ReportInDB, Depends(authorize_changes_to_report)],
) -> Dict:
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


@router.post("/{report_id}/upvote")
async def upvote(
    report_id: int,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> ReportStatInDB:
    """
    Adds or removes the user's upvote for a report.

    ## Parameters:
    - `report_id`         (int): id number of the report
    - `db`           (Database): object with database access
    - `current_user` (UserInDB): request sending user's db record

    ## Returning:
    `ReportStatInDB`: db record of the stats of the report
    """

    # check the existence of the report
    _: ReportInDB = get_report_by_id(report_id, db)

    previous_vote: VoteInDB | None = get_previous_vote(
        report_id,
        current_user.id,
        db,
    )
    report_stat: ReportStatInDB = get_report_stats(report_id, db)

    is_new_vote = False
    new_vote: VoteEdit | None = VoteEdit(
        is_upvoted=True, is_downvoted=False, timestamp=utc_now()
    )
    if previous_vote is None:
        is_new_vote = True
        report_stat.upvote_count += 1
    elif previous_vote.is_upvoted:
        new_vote = None
        report_stat.upvote_count -= 1
    elif previous_vote.is_downvoted:
        report_stat.downvote_count -= 1
        report_stat.upvote_count += 1

    stats_update = ReportStatEdit(
        view_count=report_stat.view_count,
        upvote_count=report_stat.upvote_count,
        downvote_count=report_stat.downvote_count,
    )
    record_vote(is_new_vote, report_id, current_user.id, new_vote, db)
    updated_report_stat = update_report_stats(report_id, stats_update, db)
    return updated_report_stat


@router.post("/{report_id}/downvote")
async def downvote(
    report_id: int,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> ReportStatInDB:
    """
    Adds or removes the user's downvote for a report.

    ## Parameters:
    - `report_id`         (int): id number of the report
    - `db`           (Database): object with database access
    - `current_user` (UserInDB): request sending user's db record

    ## Returning:
    `ReportStatInDB`: db record of the stats of the report
    """

    # check the existence of the report
    _: ReportInDB = get_report_by_id(report_id, db)

    previous_vote: VoteInDB | None = get_previous_vote(
        report_id,
        current_user.id,
        db,
    )
    report_stat: ReportStatInDB = get_report_stats(report_id, db)

    is_new_vote = False
    new_vote: VoteEdit | None = VoteEdit(
        is_upvoted=False, is_downvoted=True, timestamp=utc_now()
    )
    if previous_vote is None:
        is_new_vote = True
        report_stat.downvote_count += 1
    elif previous_vote.is_downvoted:
        new_vote = None
        report_stat.downvote_count -= 1
    elif previous_vote.is_upvoted:
        report_stat.upvote_count -= 1
        report_stat.downvote_count += 1

    stats_update = ReportStatEdit(
        view_count=report_stat.view_count,
        upvote_count=report_stat.upvote_count,
        downvote_count=report_stat.downvote_count,
    )
    record_vote(is_new_vote, report_id, current_user.id, new_vote, db)
    updated_report_stat = update_report_stats(report_id, stats_update, db)
    return updated_report_stat
