from typing import List

from pydantic import BaseModel


class UserBase(BaseModel):
    """
    `users` table modules are derived from this class.

    `phone_num` is used for 2FA using one-time passwords. Limited number
    of user accounts can be associated with a single mobile phone.
    `email` is used to uniquely identify a user.

    Attributes:
    `first_name` (str): first name of the user
    `last_name`  (str): last name of the user
    `phone_num`  (str): mobile phone number of the user
    `email`      (str): unique email address of the user
    """

    first_name: str
    last_name: str
    phone_num: str
    email: str


class UserInDB(UserBase):
    """
    Model representing the db record of a user.

    Attributes:
    `first_name`   (str): first name of the user
    `last_name`    (str): last name of the user
    `phone_num`    (str): mobile phone number of the user
    `email`        (str): unique email address of the user
    `id`           (int): unique id number of the user
    `tokens` (List[str]): List of active jwt tokens
    """

    id: int
    tokens: List[str] | None


class UserIn(UserBase):
    """
    Model used to get user input to create a new user.

    Attributes:
    `first_name` (str): first name of the user
    `last_name`  (str): last name of the user
    `phone_num`  (str): mobile phone number of the user
    `email`      (str): unique email address of the user
    `password`   (str): password to be used to authenticate the user
    """

    password: str


class UserOut(UserBase):
    """
    Model used in repsonses sent to the client.

    Attributes:
    `first_name` (str): first name of the user
    `last_name`  (str): last name of the user
    `phone_num`  (str): mobile phone number of the user
    `email`      (str): unique email address of the user
    `id`         (int): unique id number of the user
    """

    id: int


class UserNameEdit(BaseModel):
    """
    Model used to get user input to edit the user's name.

    Attributes:
    `first_name` (str | None = None): first name of the user
    `last_name`  (str | None = None): last name of the user
    """

    first_name: str | None = None
    last_name: str | None = None


class Token(BaseModel):
    """
    Model used to return the generated JWT to the client.

    Attributes:
    `access_token` (str): newly generated JWT
    `token_type`   (str): the type of the issued token
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Model used to store JWT payload data.

    Attributes:
    `email` (str): email in the payload of the JWT
    """

    email: str | None = None
