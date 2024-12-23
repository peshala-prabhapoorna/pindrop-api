from typing import List, Tuple

from src.dependencies import Database
from .schemas import UserInDB
from .utils import row_to_user_in_db


def get_user_by_email(
    email: str,
    db: Database,
) -> UserInDB | None:
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
    sql = (
        "UPDATE users "
        "SET tokens = %s "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    values = (tokens, user_id)
    db.cursor.execute(sql, values)
    db.connection.commit()
