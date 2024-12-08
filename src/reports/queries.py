from typing import Tuple

from fastapi import status
from fastapi.exceptions import HTTPException

from src.dependencies import Database
from src.users.schemas import UserInDB
from src.utils import utc_now
from .utils import row_to_report, row_to_report_stat, row_to_vote
from .schemas import (
    ReportEdit,
    ReportIn,
    ReportInDB,
    ReportStatEdit,
    ReportStatInDB,
    VoteEdit,
    VoteInDB,
)


def create_new_report(
    report: ReportIn,
    current_user: UserInDB,
    db: Database,
) -> ReportInDB:
    """
    Create a new record in the `reports` table of the database.

    Parameters:
    `report`       (ReportIn): user input for the data of the report
    `current_user` (UserInDB): user who is requesting to create a report
    `db`           (Database): an object with database access

    Returns:
    ReportInDB: db record of the newly created report
    """

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
    return new_report


def create_new_report_stats_record(report_id: int, db: Database) -> None:
    """
    Create a new record in the `report_stats` table of the database.
    A new `report_stats` record should be created when a new report is
    created.

    Parameters:
    `report_id` (int): id number of the newly created report
    `db`   (Database): object with database access

    Returns:
    None
    """

    sql = "INSERT INTO report_stats(report_id) VALUES (%s);"
    values = (report_id,)
    db.cursor.execute(sql, values)
    db.connection.commit()


def get_report_by_id(report_id: int, db: Database) -> ReportInDB:
    """
    Retrieves the record of the report with the given id and returns it.

    Parameters:
    `report_id` (int): id number of the report
    `db`   (Database): object with database access

    Returns:
    ReportInDB: record of the report in `reports` table
    """

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


def soft_delete_report_by_id(report_id: int, db: Database) -> Tuple:
    """
    Soft deletes the record of the report with the given id.

    Parameters:
    `report_id` (int): id number of the report
    `db`   (Database): object with database access

    Returns:
    Tuple (title, timestamp): A tuple with the title of the report and
    the time of deletion
    """

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
    return row


def edit_report_by_id(
    report_id: int,
    updated_report: ReportEdit,
    db: Database,
) -> ReportInDB:
    """
    Edits the record of the report with the given id with the provided
    data.

    Parameters:
    `report_id`             (int): id number of the report
    `updated_report` (ReportEdit): the values in this report will be
    entered to the database
    `db`               (Database): object with database access

    Returns:
    ReportInDB: record of the updated report in the `reports` table
    """

    sql = (
        "UPDATE reports "
        "SET title = %s, location = %s, directions = %s, description = %s "
        "WHERE id = %s "
        "RETURNING *;"
    )
    values = (
        updated_report.title,
        updated_report.location,
        updated_report.directions,
        updated_report.description,
        report_id,
    )
    db.cursor.execute(sql, values)
    row = db.cursor.fetchone()
    db.connection.commit()

    response_report: ReportInDB = row_to_report(row)
    return response_report


def get_previous_vote(
    report_id: int,
    user_id: int,
    db: Database,
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
