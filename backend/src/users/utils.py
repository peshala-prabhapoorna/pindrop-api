import bcrypt
import jwt
from os import getenv
from datetime import timedelta

from src.utils import utc_now
from .schemas import UserOut


JWT_SECRET = getenv("JWT_SECRET")
JWT_ALGORITHM = getenv("JWT_ALGORITHM")
JWT_TOKEN_EXPIRE_MINS = getenv("JWT_TOKEN_EXPIRE_MINS")


def row_to_user_out(row):
    user_out = UserOut(
        id=row[0],
        first_name=row[1],
        last_name=row[2],
        phone_num=row[3],
        email=row[4],
    )

    return user_out


def authenticate_user(db_cursor, username: str, password: str):
    sql = (
        "SELECT id, first_name, last_name, email, phone_num, hashed_password "
        "FROM users "
        "WHERE email = %s AND deleted_at IS NULL;"
    )
    values = (username,)
    db_cursor.execute(sql, values)
    row = db_cursor.fetchone()

    if row is None:
        return False

    login_password_bytes = password.encode("utf-8")
    hashed_password = row[5].encode("utf-8")
    result = bcrypt.checkpw(login_password_bytes, hashed_password)

    if not result:
        return False

    return row_to_user_out(row[:5])


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = utc_now() + timedelta(minutes=int(JWT_TOKEN_EXPIRE_MINS))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
