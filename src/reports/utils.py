from .schemas import ReportEdit, ReportInDB, ReportStatInDB, ReportsInDB, VoteInDB


def row_to_report(row) -> ReportInDB:
    """
    Converts a Tuple containing data of a report into a ReportInDB
    object.

    Parameters:
    `row` (Tuple):
    (`id`, `timestamp`, `user_id`, `title`, `location`, `directions`,
    `description`)

    Returns:
    ReportInDB: An object representing the db record of a report
    """

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
    """
    Converts a Tuple containing Tuple(s) with data of a report into a
    ReportsInDB object.

    Parameters:
    `row` (Tuple): (report_1, report_2, report_3, ...)

    Returns:
    ReportsInDB: An object cotaining instance(s) of ReportInDB objects
    """

    reports = []
    for row in rows:
        report = row_to_report(row)
        reports.append(report)

    return ReportsInDB(reports=reports)


def report_to_report_edit(report: ReportInDB) -> ReportEdit:
    """
    Creates a ReportEdit model from the given ReportInDB.

    Parameters:
    `report` (ReportInDB): db record of a record

    Returns:
    ReportEdit: Model created using the given report
    """

    report_edit = ReportEdit(
        title=report.title,
        location=report.location,
        directions=report.directions,
        description=report.description,
    )
    return report_edit


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
    ReportStatInDB object.

    Parameters:
    `row` (Tuple):
    (`report_id`, `view_count`, `upvote_count`, `downvote_count`)

    Returns:
    ReportStatInDB: An object representing the db record of report stats
    """

    report_stat = ReportStatInDB(
        report_id=row[0],
        view_count=row[1],
        upvote_count=row[2],
        downvote_count=row[3],
    )
    return report_stat
