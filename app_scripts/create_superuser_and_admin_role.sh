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

        async with connection.cursor() as cursor:

            # -------------------------------------
            # Ensure admin role exists
            # -------------------------------------
            check_role = "SELECT id FROM role WHERE name = 'admin' LIMIT 1"
            await cursor.execute(check_role)
            role_row = await cursor.fetchone()

            if role_row:
                admin_role_id = role_row[0]
            else:
                admin_role_id = uuid.uuid4().hex
                insert_role = f"""
                    INSERT INTO role (id, name, description)
                    VALUES ('{admin_role_id}', 'admin', 'Administrator role')
                """
                await cursor.execute(insert_role)
                print("Created 'admin' role")

            # -------------------------------------
            # Create superuser with admin role
            # -------------------------------------
            user_id = uuid.uuid4().hex
            unhashed_password = '${SUPERUSER_PASSWORD}'
            hashed_password = passwd_context.hash(unhashed_password)

            user_insert_query = f"""
            INSERT INTO user
                (id, first_name, last_name, email, password, birth_date,
                 is_active, phone_number, role_id)
            VALUES (
                '{user_id}',
                '${SUPERUSER_FIRST_NAME}',
                '${SUPERUSER_LAST_NAME}',
                '${SUPERUSER_EMAIL}',
                '{hashed_password}',
                '${SUPERUSER_BIRTHDATE}',
                TRUE,
                '${SUPERUSER_PHONE_NUMBER}',
                '{admin_role_id}'
            )
            """

            await cursor.execute(user_insert_query)
            await connection.commit()
            print("Successfully created superuser with role 'admin'")

    except asyncmy.errors.IntegrityError:
        print("Couldn't create superuser — record likely already exists.")
        sys.exit(-1)
    finally:
        await connection.close()


asyncio.run(run())

END
}

create_superuser $1

exec "$@"
