from pydantic import BaseModel


class Report(BaseModel):
    timestamp: str
    title: str
    location: str
    directions: str
    description: str
    up_votes: int
    down_votes: int


def reports_to_dict(rows):
    dicts = []
    for row in rows:
        new_dict = dict(
            zip(
                [
                    "id",
                    "timestamp",
                    "title",
                    "location",
                    "directions",
                    "description",
                    "up_votes",
                    "down_votes"
                ],
                list(row)
            )
        ) 
        dicts.append(new_dict)

    return dicts
