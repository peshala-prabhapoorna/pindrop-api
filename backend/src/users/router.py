import bcrypt
from fastapi import APIRouter

from src.utils import utc_now
from src.database import db_connection, db_cursor
from .schemas import UserIn
from .utils import row_to_user_out

router = APIRouter()


@router.post("/api/v0/users")
async def create_user(user: UserIn):
    sql = (
        "INSERT INTO users (created_at, first_name, last_name, phone_num, "
        "email, hashed_password) "
        "VALUES(%s, %s, %s, %s, %s, %s) "
        "RETURNING id, first_name, last_name, phone_num, email;"
    )
    created_at = utc_now()

    # convert password to array of bytes
    password_bytes = user.password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    values = (
        created_at,
        user.first_name,
        user.last_name,
        user.phone_num,
        user.email,
        hashed_password,
    )

    db_cursor.execute(sql, values)
    row = db_cursor.fetchone()
    db_connection.commit()

    return await row_to_user_out(row)


@router.get("/api/v0/users/{user_id}")
async def get_user(user_id: str):
    sql = (
        "SELECT id, first_name, last_name, phone_num, email "
        "FROM users "
        "WHERE id = %s;"
    )
    values = (user_id,)

    db_cursor.execute(sql, values)
    row = db_cursor.fetchone()

    if row is None:
        return {"message": "user does not exist"}

    return await row_to_user_out(row)
