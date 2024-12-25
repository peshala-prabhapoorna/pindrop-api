import bcrypt
from datetime import timedelta
import jwt
from jwt.exceptions import ExpiredSignatureError
from typing import List, Tuple

from src.utils import utc_now
from src.dependencies import Database
from .schemas import UserInDB, UserOut


def row_to_user_in_db(row: Tuple) -> UserInDB:
    """
    Converts a Tuple containing data of a user into a UserInDB object.

    Parameters:
    `row` (Tuple):
    (`id`, `first_name`, `last_name`, `phone_num`, `email`, `tokens`)

    Returns:
    UserInDB: An object representing the db record of a user
    """

    user = UserInDB(
        id=row[0],
        first_name=row[1],
        last_name=row[2],
        phone_num=row[3],
        email=row[4],
        tokens=row[5],
    )
    return user


def row_to_user_out(row: Tuple) -> UserOut:
    """
    Converts a Tuple containing data of a user into a UserOut object.

    Parameters:
    `row` (Tuple):
    (`id`, `first_name`, `last_name`, `phone_num`, `email`)

    Returns:
    UserOut: An object used to send data of a user to the client
    """

    user_out = UserOut(
        id=row[0],
        first_name=row[1],
        last_name=row[2],
        phone_num=row[3],
        email=row[4],
    )
    return user_out


def authenticate_user(
    email: str,
    password: str,
    db: Database,
) -> UserInDB | bool:
    """
    Checks whether the password provided is correct for the user
    account attached to the email.

    Attributes:
    `email` (str): Email of a user account
    `password` (str): Password for the user account

    Returns:
    UserInDB | bool: Returns user data in case of successful
    authentication and False otherwise.
    """

    sql = (
        "SELECT "
        "id, first_name, last_name, phone_num, email, tokens, hashed_password "
        "FROM users "
        "WHERE email = %s AND deleted_at IS NULL;"
    )
    values = (email,)
    db.cursor.execute(sql, values)
    row: Tuple | None = db.cursor.fetchone()

    if row is None:
        return False

    login_password_bytes = password.encode("utf-8")
    hashed_password = row[6].encode("utf-8")
    result = bcrypt.checkpw(login_password_bytes, hashed_password)

    if not result:
        return False

    return row_to_user_in_db(row[:6])


def create_access_token(data: dict, jwt_args: dict) -> str:
    """
    Creates a new access token (JWT).

    Attributes:
    `data`     (dict): Data to be embedded in the new token
    `jwt_args` (dict): JWT token related data

    Returns:
    str: Newly created token
    """

    to_encode = data.copy()
    expire = utc_now() + timedelta(minutes=int(jwt_args["timedelta"]))
    to_encode.update({"exp": expire})

    encoded_jwt: str = jwt.encode(
        to_encode, jwt_args["secret"], algorithm=jwt_args["algorithm"]
    )
    return encoded_jwt


def remove_expired_tokens(
    tokens: List[str] | None,
    jwt_args: dict,
) -> List[str] | None:
    """
    Removes expired tokens from the active tokens list.

    Attributes:
    `tokens` (List[str] | None): List of active access tokens
    `jwt_args`           (dict): JWT token related data

    Returns:
    List[str] | None: Updated list without expired tokens
    """

    if tokens is None:
        return None

    tokens_copy = tokens.copy()
    for token in tokens_copy:
        try:
            jwt.decode(
                token,
                jwt_args["secret"],
                algorithms=[jwt_args["algorithm"]],
                options={"verify_exp": True},
            )
        except ExpiredSignatureError:
            tokens.remove(token)

    return tokens
