# Pindrop API

#### [Video Demo](https://youtu.be/Kf6628NfLTk)

Pindrop API is a not yet powerful (but will soon be :D), location-based issue  
reporting and tracking tool designed for enterprises managing large-scale  
facilities, factories, or location-dependent services. This API simplifies  
the process of tracking and managing issues across extensive areas, ensuring  
operational efficiency and improved service delivery.

---

## Key Features

- Issue Reporting and Management: Create, edit, delete, and fetch reports  
related to various issues across locations.
- User Management: Handle user accounts seamlessly, including account  
creation, editing details, fetching user information, and account deletion.
- Authentication and Authorization: Secure access to protected endpoints with  
user authentication.

---

## Technology Stack

- Framework: FastAPI
- Language: Python (3.12.3)

---

## Endpoints Overview

The **Pindrop API** offers a comprehensive set of endpoints organized into key  
functionalities, enabling robust issue reporting, management, and user account  
handling. Here's a detailed overview of the available endpoints:

### Reports Management

1. **Fetch All Reports**
   - **Endpoint:** `GET /api/v0/reports`
   - **Description:** Retrieves all reports that have not been deleted.
   - **Authorization:** Not required.
   - **Caution:** This endpoint is resource-intensive and could be exploited  
   if a large number of reports are fetched simultaneously.

2. **Create a Report**
   - **Endpoint:** `POST /api/v0/reports`
   - **Description:** Creates a new issue report.
   - **Authorization:** Required.
   - **Parameters:**
     - `title` (String): Summary of the issue.
     - `location` (String): Coordinates of the issue location.
     - `directions` (String): Landmarks or tips for locating the issue.
     - `description` (String): Detailed description of the issue.

3. **Fetch a Specific Report**
   - **Endpoint:** `GET /api/v0/reports/{report_id}`
   - **Description:** Retrieves the details of a specific report.
   - **Authorization:** Not required.
   - **Path Parameter:** `report_id` (Integer).

4. **Edit a Report**
   - **Endpoint:** `PATCH /api/v0/reports/{report_id}`
   - **Description:** Updates the details of a specific report.
   - **Authorization:** Required (only for the report creator).
   - **Path Parameter:** `report_id` (Integer).
   - **Parameters:**
     - `title`, `location`, `directions`, `description` (Optional): Fields to  
     update.

5. **Delete a Report**
   - **Endpoint:** `DELETE /api/v0/reports/{report_id}`
   - **Description:** Soft-deletes a report, making it recoverable.
   - **Authorization:** Required (only for the report creator).
   - **Path Parameter:** `report_id` (Integer).

6. **Upvote a Report**
   - **Endpoint:** `POST /api/v0/reports/{report_id}/upvote`
   - **Description:** Adds or toggles an upvote for a report.
   - **Authorization:** Required.
   - **Path Parameter:** `report_id` (Integer).

7. **Downvote a Report**
   - **Endpoint:** `POST /api/v0/reports/{report_id}/downvote`
   - **Description:** Adds or toggles a downvote for a report.
   - **Authorization:** Required.
   - **Path Parameter:** `report_id` (Integer).

---

### User Management

1. **Create a User**
   - **Endpoint:** `POST /api/v0/users`
   - **Description:** Registers a new user.
   - **Authorization:** Not required.
   - **Parameters:**
     - `first_name`, `last_name`, `phone_num`, `email`, `password` (Strings).

2. **Edit User Information**
   - **Endpoint:** `PATCH /api/v0/users`
   - **Description:** Updates user details.
   - **Authorization:** Required (only for the user).
   - **Parameters:**
     - `first_name`, `last_name` (Optional Strings).

3. **Delete a User**
   - **Endpoint:** `DELETE /api/v0/users`
   - **Description:** Deletes the currently authenticated user's account.
   - **Authorization:** Required.

4. **Fetch User Information**
   - **Endpoint:** `GET /api/v0/users/{user_id}`
   - **Description:** Retrieves information about a specific user.
   - **Authorization:** Required.
   - **Path Parameter:** `user_id` (String).

5. **Login**
   - **Endpoint:** `POST /api/v0/users/token`
   - **Description:** Generates a new access token using username (email) and  
   password.
   - **Authorization:** Not required.

6. **Logout**
   - **Endpoint:** `DELETE /api/v0/users/token`
   - **Description:** Invalidates the current access token.
   - **Authorization:** Required.

These endpoints, coupled with secure authentication via  
`OAuth2PasswordBearer`, form the backbone of the Pindrop API. They provide  
flexibility and scalability for handling complex location-based issue tracking  
scenarios.

---

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

The API comes with an interactive SwaggerUI interface where all endpoints can  
be accessed and tested directly.

Happy coding!

---

## Future Plans

- Enhancing feature richness.
- Developing a user-friendly UI for easier interaction.

---

## Author

This project is developed by Prabhapoorna.

Feel free to contribute, report issues, or share feedback!
