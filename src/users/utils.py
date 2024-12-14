import bcrypt
from datetime import timedelta
import jwt
from jwt.exceptions import ExpiredSignatureError
from typing import List, Tuple

from src.utils import utc_now
from src.dependencies import Database
from .schemas import UserInDB, UserOut


def row_to_user_in_db(row: Tuple) -> UserInDB:
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
    user_out = UserOut(
        id=row[0],
        first_name=row[1],
        last_name=row[2],
        phone_num=row[3],
        email=row[4],
    )
    return user_out


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


def authenticate_user(
    email: str,
    password: str,
    db: Database,
) -> UserInDB | bool:
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
