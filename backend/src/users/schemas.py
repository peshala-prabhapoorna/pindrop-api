from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    first_name : str
    last_name : str
    phone_num : str
    email : str


# model to create a user
class UserIn(UserBase):
    created_at : datetime
    password : str
