from typing import Tuple

from fastapi import HTTPException, status

from src.dependencies import Database
from .schemas import (
    ReportInDB,
    ReportStatEdit,
    ReportStatInDB,
    ReportsInDB,
    VoteEdit,
    VoteInDB,
)


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


def row_to_vote(row) -> VoteInDB:
    """
    Converts a Tuple containing data of a vote into a VoteInDB object.

    Parameters:
    `row` (Tuple):
    (`report_id`, `user_id`, `is_upvoted`, `is_downvoted`, `timestamp`)

    Returns:
    VoteInDB: An object representing the database record of a vote.
    """

    vote = VoteInDB(
        report_id=row[0],
        user_id=row[1],
        is_upvoted=row[2],
        is_downvoted=row[3],
        timestamp=row[4],
    )
    return vote


def row_to_report_stat(row) -> ReportStatInDB:
    """
    Converts a Tuple containing statistics data of a report into a
    ReportInDB object.

    Parameters:
    `row` (Tuple):
    (`report_id`, `view_count`, `upvote_count`, `downvote_count`)

    Returns:
    ReportInDB: An object representing the db record of report stats
    """

    report_stat = ReportStatInDB(
        report_id=row[0],
        view_count=row[1],
        upvote_count=row[2],
        downvote_count=row[3],
    )
    return report_stat


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


def get_previous_vote(
    report_id: int, user_id: int, db: Database
) -> VoteInDB | None:
    """
    Retrieves the record of the last vote casted by the user on the
    report and returns it.

    Parameters:
    `report_id` (int): id number of the report
    `user_id`   (int): id number of the user
    `db`   (Database): object with database access

    Returns:
    VoteInDB: record of the last vote in `votes` table
    """

    sql = "SELECT * FROM votes WHERE report_id = %s AND user_id = %s;"
    values = (report_id, user_id)
    db.cursor.execute(sql, values)
    row: Tuple | None = db.cursor.fetchone()

    if row is None:
        return None

    vote: VoteInDB = row_to_vote(row)
    return vote


def get_report_stats(report_id: int, db: Database) -> ReportStatInDB:
    """
    Retrieves the stats record of the respective report and returns it.

    Parameters:
    `report_id` (int): id number of the report
    `db`   (Database): object with database access

    Returns:
    ReportStatInDB: stats record of the report in `report_stats` table
    """

    sql = "SELECT * FROM report_stats WHERE report_id = %s;"
    values = (report_id,)
    db.cursor.execute(sql, values)
    row: Tuple | None = db.cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report stats do not exist",
        )

    report_stats: ReportStatInDB = row_to_report_stat(row)
    return report_stats


def update_report_stats(
    report_id: int,
    stats_update: ReportStatEdit,
    db: Database,
) -> ReportStatInDB:
    """
    Updates the stats of the respective report in the db and returns
    the updated report stats.

    Parameters:
    `report_id`               (int): id number of the report
    `stats_update` (ReportStatEdit): an object with the updated stats
    `db`                 (Database): object with database access

    Returns:
    ReportStatInDB: the updated record in the database
    """

    sql = (
        "UPDATE report_stats "
        "SET view_count = %s, upvote_count = %s, downvote_count = %s "
        "WHERE report_id = %s "
        "RETURNING *;"
    )
    values = (
        stats_update.view_count,
        stats_update.upvote_count,
        stats_update.downvote_count,
        report_id,
    )
    db.cursor.execute(sql, values)
    row = db.cursor.fetchone()
    db.connection.commit()

    report_stats: ReportStatInDB = row_to_report_stat(row)
    return report_stats


def record_vote(
    is_new_vote: bool,
    report_id: int,
    user_id: int,
    vote_data: VoteEdit | None,
    db: Database,
) -> None:
    """
    Update or insert record of the vote in the db.

    Parameters:
    `is_new_vote`          (bool): True if first vote, False otherwise
    `report_id`             (int): id number of the report
    `user_id`               (int): id number of the user
    `vote_data` (VoteEdit | None): object with data of the new vote or
    if removing vote `None`
    `db`               (Database): object with database access
    """

    if vote_data is None:
        sql = "DELETE FROM votes WHERE report_id = %s AND user_id = %s;"
        values = (report_id, user_id)
    elif is_new_vote:
        sql = "INSERT INTO votes VALUES (%s, %s, %s, %s, %s);"
        values = (
            report_id,
            user_id,
            vote_data.is_upvoted,
            vote_data.is_downvoted,
            vote_data.timestamp,
        )
    else:
        sql = (
            "UPDATE votes "
            "SET is_upvoted = %s, is_downvoted = %s, timestamp = %s "
            "WHERE report_id = %s AND user_id = %s;"
        )
        values = (
            vote_data.is_upvoted,
            vote_data.is_downvoted,
            vote_data.timestamp,
            report_id,
            user_id,
        )
    db.cursor.execute(sql, values)
    db.connection.commit()
    return None
