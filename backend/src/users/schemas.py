from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: str
    phone_num: str
    email: str


# model to create a user
class UserIn(UserBase):
    password: str


# model to use in responses
class UserOut(UserBase):
    id: int


class UserNameEdit(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
