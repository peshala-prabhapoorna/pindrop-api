from datetime import datetime
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
    user_id: int
    up_votes: int
    down_votes: int


# model to get input for report updates/edits
class ReportEdit(ReportBase):
    title: str | None = None
    location: str | None = None
    directions: str | None = None
    description: str | None = None


# mode to use in reponses that sends multiple reports
class ReportsOut(BaseModel):
    reports: list[ReportOut]
