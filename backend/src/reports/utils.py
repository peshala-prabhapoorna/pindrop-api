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
        up_votes=row[7],
        down_votes=row[8],
    )

    return report


def rows_to_reports(rows):
    reports = []
    for row in rows:
        report = row_to_report(row)
        reports.append(report)

    return ReportsInDB(reports=reports)
