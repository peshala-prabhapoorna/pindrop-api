import psycopg2.extensions
from fastapi.security import OAuth2PasswordBearer

from .database import db_connection, db_cursor


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v0/users/token")


class Database:
    def __init__(self):
        self.connection: psycopg2.extensions.connection = db_connection
        self.cursor: psycopg2.extensions.connection = db_cursor
