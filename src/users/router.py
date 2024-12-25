from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.utils import utc_now
from src.dependencies import Database, oauth2_scheme
from .dependencies import get_current_active_user, get_jwt_env_vars
from .schemas import UserIn, UserInDB, UserNameEdit, Token, UserOut
from .queries import update_jwt_tokens
from .utils import (
    row_to_user_out,
    authenticate_user,
    create_access_token,
    remove_expired_tokens,
)

router = APIRouter(prefix="/api/v0/users", tags=["users"])


@router.post(
    "",
    summary="Create a user",
    response_description="Newly created user",
)
async def create_user(
    user: UserIn,
    db: Annotated[Database, Depends(Database)],
) -> UserOut:
    """
    Create a new report.

    Phone number and email can only be attached to one account.

    No authorization required.

    - **first_name**: First name of the user
    - **last_name**: Last name of the user
    - **phone_num**: Phone number of the user
    - **email**: Email address of the user
    - **password**: Password of the user
    """

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

    db.cursor.execute(sql, values)
    row = db.cursor.fetchone()
    db.connection.commit()

    return row_to_user_out(row)


@router.post(
    "/token",
    summary="Login",
    response_description="Newly created access token",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    jwt_env: Annotated[dict, Depends(get_jwt_env_vars)],
    db: Annotated[Database, Depends(Database)],
) -> Token:
    """
    Login by providing username(email) and password.

    No authorization required.
    """

    user = authenticate_user(form_data.username, form_data.password, db)
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

    update_jwt_tokens(user.tokens, user.id, db)

    return Token(access_token=access_token, token_type="bearer")


@router.delete(
    "/token",
    summary="Logout",
    response_description="Session termination message",
)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    db: Annotated[Database, Depends(Database)],
) -> dict:
    """
    Logout of the session and deactivate access token.

    Only signed in users are authorized to use this endpoint.
    """

    current_user.tokens.remove(token)
    update_jwt_tokens(current_user.tokens, current_user.id, db)
    return {"detail": "Session terminated"}


@router.get(
    "/{user_id}",
    summary="Get user info",
    response_description="Information of user requested",
)
async def get_user(
    user_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    db: Annotated[Database, Depends(Database)],
) -> UserOut | dict:
    """
    Fetch data of a user.

    Only signed in users are authorized to use this endpoint.

    - **user_id**: ID number of the user being requested
    """

    sql = (
        "SELECT id, first_name, last_name, phone_num, email "
        "FROM users "
        "WHERE id = %s AND deleted_at IS NULL;"
    )
    values = (user_id,)

    db.cursor.execute(sql, values)
    row = db.cursor.fetchone()

    if row is None:
        return {"message": "user does not exist"}

    return row_to_user_out(row)


@router.patch(
    "",
    summary="Edit user information",
    response_description="User information after update",
)
async def edit_user_name(
    user_names: UserNameEdit,
    user: Annotated[UserInDB, Depends(get_current_active_user)],
    db: Annotated[Database, Depends(Database)],
) -> UserOut | dict:
    """
    Edit information of the user.

    Only the owner of the account is authorized to use this endpoint.

    - **first_name**: New first name of the user
    - **last_name**: New last name of the user
    """

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
    db.cursor.execute(update_sql, update_values)
    row = db.cursor.fetchone()
    db.connection.commit()

    return row_to_user_out(row)


@router.delete(
    "",
    summary="Delete user account",
    response_description="status report of user account deletion",
)
async def delete_user(
    user: Annotated[UserInDB, Depends(get_current_active_user)],
    db: Annotated[Database, Depends(Database)],
) -> dict:
    """
    Delete user account of the current active user.

    Only the owner of the account is authorized to use this endpoint.
    """

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

    db.cursor.execute(sql, values)
    row = db.cursor.fetchone()
    db.connection.commit()

    if row is None:
        return {"message": "failed to delete user account"}

    response = {
        "message": "user deleted",
        "first_name": row[0],
        "last_name": row[1],
        "deleted_at": row[2],
    }

    return response
