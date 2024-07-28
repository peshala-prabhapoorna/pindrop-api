from datetime import datetime
from pydantic import BaseModel


class Report(BaseModel):
    id: int = None
    timestamp: datetime
    title: str
    location: str
    directions: str
    description: str
    up_votes: int
    down_votes: int
    deleted_at: datetime = None


class Reports(BaseModel):
    reports: list[Report]


def rows_to_reports(rows):
    reports = []
    for row in rows:
        report = Report(
            id=row[0],
            timestamp=row[1],
            title=row[2],
            location=row[3],
            directions=row[4],
            description=row[5],
            up_votes=row[6],
            down_votes=row[7],
        )
        reports.append(report)

    return Reports(reports=reports)
