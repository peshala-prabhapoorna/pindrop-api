from .schemas import ReportInDB, ReportStatInDB, ReportsInDB, VoteInDB


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


def rows_to_reports(rows) -> ReportsInDB:
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
