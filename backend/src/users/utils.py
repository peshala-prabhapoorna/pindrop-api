import bcrypt
from datetime import timedelta
import jwt

from src.utils import utc_now
from .schemas import UserOut


def row_to_user_out(row):
    user_out = UserOut(
        id=row[0],
        first_name=row[1],
        last_name=row[2],
        phone_num=row[3],
        email=row[4],
    )

    return user_out


def get_user(db_cursor, email: str):
    sql = (
        "SELECT id, first_name, last_name, phone_num, email "
        "FROM users "
        "WHERE email = %s AND deleted_at IS NULL;"
    )
    values = (email,)
    db_cursor.execute(sql, values)
    row = db_cursor.fetchone()

    if row is None:
        return None

    return row_to_user_out(row)


def authenticate_user(db_cursor, email: str, password: str):
    sql = (
        "SELECT id, first_name, last_name, phone_num, email, hashed_password "
        "FROM users "
        "WHERE email = %s AND deleted_at IS NULL;"
    )
    values = (email,)
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


def create_access_token(data: dict, jwt_args: dict):
    to_encode = data.copy()
    expire = utc_now() + timedelta(minutes=int(jwt_args["timedelta"]))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        jwt_args["secret"],
        algorithm=jwt_args["algorithm"]
    )
    return encoded_jwt
