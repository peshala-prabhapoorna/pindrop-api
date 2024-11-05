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
class ReportInDB(ReportBase):
    id: int
    timestamp: datetime
    user_id: int


# model to get input for report updates/edits
class ReportEdit(BaseModel):
    title: str | None = None
    location: str | None = None
    directions: str | None = None
    description: str | None = None


# mode to use in reponses that sends multiple reports
class ReportsInDB(BaseModel):
    reports: list[ReportInDB]
