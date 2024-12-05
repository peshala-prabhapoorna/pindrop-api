from datetime import datetime
from pydantic import BaseModel


class ReportBase(BaseModel):
    """
    `reports` table models are derived from this class.

    Attributes:
    `title`       (str): a short topic summarising the issue
    `location`    (str): coordinates of the location of the report
    `directions`  (str): landmarks/tips to locate the issue
    `description` (str): a detailed report of the issue
    """

    title: str
    location: str
    directions: str
    description: str


class ReportIn(ReportBase):
    """
    Model used to get input from the user to create a report.

    Attributes:
    `title`       (str): a short topic summarising the issue
    `location`    (str): coordinates of the location of the report
    `directions`  (str): landmarks/tips to locate the issue
    `description` (str): a detailed report of the issue
    """

    pass


class ReportInDB(ReportBase):
    """
    Model representing the db record of a report.

    Attributes:
    `title`          (str): a short topic summarising the issue
    `location`       (str): coordinates of the location of the report
    `directions`     (str): landmarks/tips to locate the issue
    `description`    (str): a detailed report of the issue
    `id`             (int): unique id number of the report
    `timestamp` (datetime): timestamp of when the report was created
    `user_id`        (int): id of the user who created the report
    """

    id: int
    timestamp: datetime
    user_id: int


class ReportEdit(BaseModel):
    """
    Model used to get input from the user to edit a report.

    Attributes:
    `title`       (str | None = None): a short topic summarising the
    issue
    `location`    (str | None = None): coordinates of the location of
    the report
    `directions`  (str | None = None): landmarks/tips to locate the
    issue
    `description` (str | None = None): a detailed report of the issue
    """

    title: str | None = None
    location: str | None = None
    directions: str | None = None
    description: str | None = None


class ReportsInDB(BaseModel):
    """
    Model to use in responses that send multiple reports.

    Attributes:
    `reports` (list[ReportInDB]): a list of ReportInDB objects
    """
    reports: list[ReportInDB]


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
