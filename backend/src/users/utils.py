from .schemas import UserOut


async def row_to_user_out(row):
    user_out = UserOut(
        id = row[0],
        first_name = row[1],
        last_name = row[2],
        phone_num = row[3],
        email = row[4]
    )

    return user_out
