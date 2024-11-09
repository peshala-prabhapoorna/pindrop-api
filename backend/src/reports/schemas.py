from datetime import datetime
from pydantic import BaseModel


# `reports` table models
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


# model to use in reponses that sends multiple reports
class ReportsInDB(BaseModel):
    reports: list[ReportInDB]


# `votes` table models
class VoteBase(BaseModel):
    """
    `votes` table models are derived from this class.

    Attributes:
    `is_upvoted`    (bool): records an upvote
    `is_downvoted`  (bool): records a downvote
    `timestamp` (datetime): date and time of the last update
    """

    is_upvoted: bool
    is_downvoted: bool
    timestamp: datetime


class VoteInDB(VoteBase):
    """
    Model representing the db record of a vote.

    Attributes:
    `report_id`      (int): id number of the report beging voted on
    `user_id`        (int): id number of the user casting the vote
    `is_upvoted`    (bool): records an upvote
    `is_downvoted`  (bool): records a downvote
    `timestamp` (datetime): date and time of the last update
    """

    report_id: int
    user_id: int


class VoteEdit(VoteBase):
    """
    Model used when recording a casted vote.

    Attributes:
    `is_upvoted`    (bool): records an upvote
    `is_downvoted`  (bool): records a downvote
    `timestamp` (datetime): date and time of the last update
    """

    pass


# `report_stats` table models
class ReportStatBase(BaseModel):
    """
    `reports` table models are derived from this class.

    Attributes:
    `view_count`     (int): number of times the report has been viewed
    `upvote_count`   (int): number of upvoted casted
    `downvote_count` (int): number of downvotes casted
    """

    view_count: int
    upvote_count: int
    downvote_count: int


class ReportStatInDB(ReportStatBase):
    """
    Model representing the db record of the statistics related to a
    report.

    Attributes:
    `report_id`      (int): id number of the report in `reports` table
    `view_count`     (int): number of times the report has been viewed
    `upvote_count`   (int): number of upvoted casted
    `downvote_count` (int): number of downvotes casted
    """

    report_id: int


class ReportStatEdit(ReportStatBase):
    """
    Model used when updating the statistics related to a report.

    Attributes:
    `view_count`     (int): number of times the report has been viewed
    `upvote_count`   (int): number of upvoted casted
    `downvote_count` (int): number of downvotes casted
    """

    pass
