from pydantic import BaseModel


class Report(BaseModel):
    timestamp: str
    title: str
    location: str
    directions: str
    description: str
    up_votes: int
    down_votes: int
