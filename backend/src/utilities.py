from datetime import datetime, UTC
from pydantic import BaseModel


class ReportBase(BaseModel):
    title: str
    location: str
    directions: str
    description: str


# model to get input from the user
class ReportIn(ReportBase):
    pass


# model to use in responses
class ReportOut(ReportBase):
    id: int
    timestamp: datetime
    up_votes: int
    down_votes: int


class ReportEdit(ReportBase):
    title: str | None = None
    location: str | None = None
    directions: str | None = None
    description: str | None = None


# mode to use in reponses that sends multiple reports
class ReportsOut(BaseModel):
    reports: list[ReportOut]


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


def utc_now():
    return datetime.now(UTC)
