from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.utils import utc_now
from src.database import db_connection, db_cursor
from src.dependencies import oauth2_scheme
from .dependencies import get_current_active_user, get_jwt_env_vars
from .schemas import UserIn, UserInDB, UserNameEdit, Token
from .utils import (
    row_to_user_out,
    authenticate_user,
    create_access_token,
    remove_expired_tokens,
)

router = APIRouter(prefix="/api/v0/users", tags=["users"])


@router.post("")
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


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    jwt_env: Annotated[dict, Depends(get_jwt_env_vars)],
) -> Token:
    user = authenticate_user(db_cursor, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email}, jwt_args=jwt_env
    )
    user.tokens = remove_expired_tokens(user.tokens, jwt_env)
    if user.tokens is None:
        user.tokens = [access_token]
    else:
        user.tokens.append(access_token)

    sql = (
        "UPDATE users "
        "SET tokens = %s "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    values = (user.tokens, user.id)
    db_cursor.execute(sql, values)
    db_connection.commit()

    return Token(access_token=access_token, token_type="bearer")


@router.delete("/token")
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    current_user.tokens.remove(token)
    sql = (
        "UPDATE users "
        "SET tokens = %s "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    values = (
        current_user.tokens,
        current_user.id,
    )
    db_cursor.execute(sql, values)
    db_connection.commit()
    return {"detail": "Session terminated"}


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
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


@router.patch("")
async def edit_user_name(
    user_names: UserNameEdit,
    user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    update_data = user_names.model_dump(exclude_unset=True)
    if update_data == {}:
        return {"message": "no new values to update"}

    name_model = UserNameEdit(
        first_name=user.first_name,
        last_name=user.last_name,
    )
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
        user.id,
    )
    db_cursor.execute(update_sql, update_values)
    row = db_cursor.fetchone()
    db_connection.commit()

    return row_to_user_out(row)


@router.delete("")
async def delete_user(
    user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    sql = (
        "UPDATE users "
        "SET tokens = '{}'::TEXT[], deleted_at = %s "
        "WHERE id = %s AND deleted_at IS NULL "
        "RETURNING first_name, last_name, deleted_at;"
    )
    values = (
        utc_now(),
        user.id,
    )

    db_cursor.execute(sql, values)
    row = db_cursor.fetchone()
    db_connection.commit()

    if row is None:
        return {"message": "failed to delete user account"}

    response = {
        "message": "user deleted",
        "first_name": row[0],
        "last_name": row[1],
        "deleted_at": row[2],
    }

    return response
