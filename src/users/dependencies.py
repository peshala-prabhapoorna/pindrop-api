import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from os import getenv
from typing import Annotated

from src.dependencies import Database, oauth2_scheme
from .queries import get_user_by_email
from .schemas import TokenData, UserInDB


async def get_jwt_env_vars():
    """
    Import environment variables related to JWT authentication.

    Returns:
    Dict: A dictionary with data related to JWT authentication
    """

    JWT_SECRET = getenv("JWT_SECRET")
    JWT_ALGORITHM = getenv("JWT_ALGORITHM")
    JWT_TOKEN_EXPIRE_MINS = getenv("JWT_TOKEN_EXPIRE_MINS")

    dict = {
        "secret": JWT_SECRET,
        "algorithm": JWT_ALGORITHM,
        "timedelta": JWT_TOKEN_EXPIRE_MINS,
    }
    return dict


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwt_env: Annotated[dict, Depends(get_jwt_env_vars)],
    db: Annotated[Database, Depends(Database)],
) -> UserInDB:
    """
    Checks the validity of the token in the request header and
    authenticates the user.

    Dependencies:
    `token`    (str): JWT token sent in the request header
    `jwt_env` (dict): environment variables related to jwt
    `db`  (Database): object with database access

    Returns:
    UserInDB: Db record of the authenticated user in the `users` table
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, jwt_env["secret"], algorithms=[jwt_env["algorithm"]]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_email(token_data.email, db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> UserInDB:
    """
    Authenticates the user and checks if the token in the request header
    is an active token.

    Active tokens are stored in the `tokens` column of `users` table.

    Dependencies:
    `token`             (str): JWT token sent in the request header
    `current_user` (UserInDB): User record returned after authenticating
    the JWT token

    Returns:
    UserInDB: Db record of the authenticated user in the `users` table
    """

    if token not in current_user.tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
