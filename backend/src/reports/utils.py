from .schemas import ReportOut, ReportsOut


def row_to_report(row):
    report = ReportOut(
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

    return ReportsOut(reports=reports)
