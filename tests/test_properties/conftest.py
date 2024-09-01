import subprocess

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.apps.properties.enums import PropertyStatusEnum
from src.apps.properties.schemas import PropertyInputSchema, PropertyOutputSchema
from src.apps.properties.services import (
    change_property_owner,
    create_property,
    get_all_properties,
)
from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.core.factory.property_factory import PropertyInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_users.conftest import db_staff_user, db_superuser, db_user

DB_PROPERTIES_SCHEMAS = [
    PropertyInputSchemaFactory().generate(property_status=PropertyStatusEnum.AVAILABLE)
    for _ in range(2)
]
DB_PROPERTIES_SCHEMAS.append(
    PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.UNAVAILABLE
    )
)


"""
one property will be unavailable
and 2 of them will have the ownership (staff user and superuser)
"""


@pytest_asyncio.fixture
async def db_properties(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_superuser: UserOutputSchema,
) -> PagedResponseSchema[PropertyOutputSchema]:
    properties = [
        await create_property(async_session, property_input)
        for property_input in DB_PROPERTIES_SCHEMAS
    ]
    await change_property_owner(
        async_session, UserIdSchema(id=db_staff_user.id), properties[0].id
    )
    await change_property_owner(
        async_session, UserIdSchema(id=db_superuser.id), properties[1].id
    )
    return await get_all_properties(
        async_session, PageParams(), output_schema=PropertyOutputSchema
    )
