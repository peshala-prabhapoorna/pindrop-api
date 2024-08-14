from .schemas import ReportOut, ReportsOut


def row_to_report(row):
    report = ReportOut(
        id=row[0],
        timestamp=row[1],
        title=row[2],
        location=row[3],
        directions=row[4],
        description=row[5],
        up_votes=row[6],
        down_votes=row[7],
    )

    return report


def rows_to_reports(rows):
    reports = []
    for row in rows:
        report = row_to_report(row)
        reports.append(report)

    return ReportsOut(reports=reports)
