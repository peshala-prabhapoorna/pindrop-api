CREATE EXTENSION citext;
CREATE DOMAIN email AS citext
    CHECK (
        VALUE ~ '^[a-zA-Z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
);

CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    first_name VARCHAR(32) NOT NULL,
    last_name  VARCHAR(32) NOT NULL,
    phone_num  VARCHAR(9) NOT NULL UNIQUE,
    email      email NOT NULL UNIQUE,
    password   VARCHAR(64) NOT NULL,
    deleted_at TIMESTAMP DEFAULT NULL,
    token      TEXT DEFAULT NULL
);
