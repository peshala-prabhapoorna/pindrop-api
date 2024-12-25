from typing import List, Tuple

from src.dependencies import Database
from .schemas import UserInDB
from .utils import row_to_user_in_db


def get_user_by_email(
    email: str,
    db: Database,
) -> UserInDB | None:
    """
    Retrieves user information from the database with the given email
    and returns them.

    Attributes:
    `email`   (str): Email of the requested user
    `db` (Database): Object with database access

    Returns:
    UserInDB | None: Returns user info if user exists in database or
    None otherwise.
    """

    sql = (
        "SELECT id, first_name, last_name, phone_num, email, tokens "
        "FROM users "
        "WHERE email = %s AND deleted_at IS NULL;"
    )
    values = (email,)
    db.cursor.execute(sql, values)
    row: Tuple | None = db.cursor.fetchone()

    if row is None:
        return None

    return row_to_user_in_db(row)


def update_jwt_tokens(
    tokens: List[str],
    user_id: int,
    db: Database,
) -> None:
    """
    Updates the active access tokens in the database.

    Attributes:
    `tokens` (List[str]): List of active access tokens
    `user_id`      (int): ID number of the user account
    `db`      (Database): Object with database access
    """

    sql = (
        "UPDATE users "
        "SET tokens = %s "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    values = (tokens, user_id)
    db.cursor.execute(sql, values)
    db.connection.commit()
