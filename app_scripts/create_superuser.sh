#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

create_superuser() {
python << END
import sys
import asyncio
import uuid

import asyncmy
from passlib.context import CryptContext

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def run():
    try:
        db_name = "${TEST_MYSQL_DB}" if "$1" == "test" else "${MYSQL_DB}"
        
        connection = await asyncmy.connect(
            database=db_name,
            user="${MYSQL_ROOT_USER}",
            password="${MYSQL_ROOT_PASSWORD}",
            host="${MYSQL_HOST}",
            port=${MYSQL_PORT}
        )

        user_id = uuid.uuid4().hex
        unhashed_password = '${SUPERUSER_PASSWORD}'
        hashed_password = passwd_context.hash(unhashed_password)

        user_insert_query = f"""
        INSERT INTO user
            (id, first_name, last_name, email, password, birth_date,
            is_superuser, is_staff, is_active, phone_number)
        VALUES (
            '{user_id}',
            '${SUPERUSER_FIRST_NAME}',
            '${SUPERUSER_LAST_NAME}',
            '${SUPERUSER_EMAIL}',
            '{hashed_password}',
            '${SUPERUSER_BIRTHDATE}',
            TRUE,
            TRUE,
            TRUE,
            '${SUPERUSER_PHONE_NUMBER}'
        )
        """
        async with connection.cursor() as cursor:
            await cursor.execute(user_insert_query)
            await connection.commit()

        print("Successfully created superuser")

    except asyncmy.errors.IntegrityError as e:
        print("Couldn't create a superuser. Check if the superuser account is already created.")
        sys.exit(-1)
    finally:
        await connection.close()

asyncio.run(run())

END
}

create_superuser $1

exec "$@"
