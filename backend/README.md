# Backend API with FastAPI

Python version - 3.12.3

## Get started: for devs

1. Spin up a virtual environment in `/backend/`. We're using `virtualenv`.

>[!WARNING]
>Instructions below assume that your working directory is `/backend/`

```bash
virtualenv venv
source venv/bin/activate
```

2. Install dependencies

```bash
pip3 install -r requirements.txt
```

Installing dependencies using the requirements file has not worked well for
me so far. So, if it fails, **install each dependency one by one**. Some
dependencies require more than a simple `pip` install.

   - fastapi

`pip` install command is different. Refer the FastAPI docs.

```bash
pip install "fastapi[standard]"
```

   - psycopg2

`python3-devel`, `libpg-devel` libraries are required. The exat names of the
libraries depend on the OS or the Linux distribution. Look it up!

   - pyjwt
   - bcrypt

`pip` install command is different. Refer the FastAPI authorization docs.

```bash
pip install "passlib[bcrypt]"
```


3. Setup PostgreSQL database

    1. Initiate Postgresql.
    2. Add password to default user (postgres).
    3. Create new user with password (admin of the pindrop database).
    4. Alter newly created user with appropriate privileges (user roles).
    5. Change the authentication mode form `peer` to `md5`.
    6. Login to the database as the new user.
    7. Create database for pindrop.
    8. Create a user to be used by the api.
    9. Grant relevant privileges to the newly created user.

4. Fill in the values of config files

Sample config files are given. Copy them and fill in the values.

   - .env.sample
   - database/database.ini

5. Run the backend application using fastapi cli

```bash
fastapi dev app/main.py
```

Happy coding!
