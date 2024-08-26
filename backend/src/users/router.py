from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.utils import utc_now
from src.database import db_connection, db_cursor
from .schemas import UserIn, UserNameEdit, Token
from .utils import row_to_user_out, authenticate_user, create_access_token

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
        hashed_password.decode("utf-8"),
    )

    db_cursor.execute(sql, values)
    row = db_cursor.fetchone()
    db_connection.commit()

    return row_to_user_out(row)


@router.get("/api/v0/users/{user_id}")
async def get_user(user_id: str):
    sql = (
        "SELECT id, first_name, last_name, phone_num, email "
        "FROM users "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    values = (user_id,)

    db_cursor.execute(sql, values)
    row = db_cursor.fetchone()

    if row is None:
        return {"message": "user does not exist"}

    return row_to_user_out(row)


@router.patch("/api/v0/users/{user_id}")
async def edit_user_name(user_id: str, user_names: UserNameEdit):
    update_data = user_names.model_dump(exclude_unset=True)
    if update_data == {}:
        return {"message": "no new values to update"}

    select_sql = (
        "SELECT first_name, last_name "
        "FROM users "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    db_cursor.execute(select_sql, (user_id,))
    row = db_cursor.fetchone()

    if row is None:
        return {"message": "user does not exist"}

    name_model = UserNameEdit(first_name=row[0], last_name=row[1])
    updated_name_model = name_model.model_copy(update=update_data)

    update_sql = (
        "UPDATE users "
        "SET first_name = %s, last_name = %s "
        "WHERE id = %s AND deleted_at IS NULL "
        "RETURNING id, first_name, last_name, phone_num, email;"
    )
    update_values = (
        updated_name_model.first_name,
        updated_name_model.last_name,
        user_id,
    )
    db_cursor.execute(update_sql, update_values)
    row = db_cursor.fetchone()
    db_connection.commit()

    return row_to_user_out(row)


@router.delete("/api/v0/users/{user_id}")
async def delete_user(user_id: str):
    sql = (
        "UPDATE users "
        "SET deleted_at = %s "
        "WHERE id = %s AND deleted_at IS NULL "
        "RETURNING first_name, last_name, deleted_at;"
    )
    values = (
        utc_now(),
        user_id,
    )

    db_cursor.execute(sql, values)
    row = db_cursor.fetchone()
    db_connection.commit()

    if row is None:
        return {"message": "user does not exist"}

    response = {
        "message": "user deleted",
        "first_name": row[0],
        "last_name": row[1],
        "deleted_at": row[2],
    }

    return response


@router.post("/api/v0/users/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = authenticate_user(db_cursor, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})

    sql = (
        "UPDATE users "
        "SET token = %s "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    values = (access_token, user.id)
    db_cursor.execute(sql, values)
    db_connection.commit()

    return Token(access_token=access_token, token_type="bearer")
