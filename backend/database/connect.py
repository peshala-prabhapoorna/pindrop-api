import psycopg2
from config import load_config


def connect():
    config = load_config()
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as connection:
            print("Connected to the PostgreSQL server")
            return connection
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


if __name__ == "__main__":
    connect()
