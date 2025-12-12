import asyncio
from fastapi import BackgroundTasks

from src.database.db_connection import async_session 
from src.core.factory.user_factory import UserRegisterSchemaFactory

from src.apps.users.services.user_services import create_single_user, create_role, set_user_role
from src.apps.users.schemas import RoleInputSchema


async def seed_data():
    async with async_session() as session:

        # ---------------------------------------------------------
        # 1. Create roles with descriptions
        # ---------------------------------------------------------

        roles_to_create = {
            "staff": "Internal staff member with elevated permissions",
            "user": "Regular end-user with basic access",
        }

        created_roles = {}

        for name, description in roles_to_create.items():
            role_input = RoleInputSchema(
                name=name,
                description=description
            )
            role = await create_role(session, role_input=role_input)
            created_roles[name] = role

        print("Roles created:", list(created_roles.keys()))

        # ---------------------------------------------------------
        # 2. Generate users via factory
        # ---------------------------------------------------------

        user_factory = UserRegisterSchemaFactory()

        # Create staff users
        for _ in range(2):
            schema = user_factory.generate()
            user = await create_single_user(session, schema, BackgroundTasks())
            user = await set_user_role(session, user.id, "staff")

        # Create normal users
        for _ in range(3):
            schema = user_factory.generate()
            user = await create_single_user(session, schema, BackgroundTasks())

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_data())
