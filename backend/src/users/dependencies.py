import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from os import getenv
from typing import Annotated

from src.database import db_cursor
from src.dependencies import oauth2_scheme
from .schemas import TokenData
from .utils import get_user


async def get_jwt_env_vars():
    JWT_SECRET = getenv("JWT_SECRET")
    JWT_ALGORITHM = getenv("JWT_ALGORITHM")
    JWT_TOKEN_EXPIRE_MINS = getenv("JWT_TOKEN_EXPIRE_MINS")
    
    dict = {
        "secret": JWT_SECRET,
        "algorithm": JWT_ALGORITHM,
        "timedelta": JWT_TOKEN_EXPIRE_MINS
    }
    return dict
    

async def get_current_active_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwt_env: Annotated[dict, Depends(get_jwt_env_vars)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            jwt_env["secret"],
            algorithms=[jwt_env["algorithm"]]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db_cursor, token_data.email)
    if user is None:
        raise credentials_exception
    return user
