import subprocess

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.apps.properties.schemas import PropertyOutputSchema, PropertyInputSchema
from src.apps.properties.services import create_property, change_property_owner, get_all_properties
from src.core.factory.property_factory import (
    PropertyInputSchemaFactory
)
from src.apps.properties.enums import PropertyStatusEnum
from src.apps.users.schemas import UserOutputSchema, UserIdSchema
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_users.conftest import db_user, db_staff_user

DB_PROPERTIES_SCHEMAS = [
    PropertyInputSchemaFactory().generate(property_status=PropertyStatusEnum.AVAILABLE)
    for _ in range(3)
]
DB_PROPERTIES_SCHEMAS.append(
    PropertyInputSchemaFactory().generate(property_status=PropertyStatusEnum.UNAVAILABLE)
)


"""
the last property will be unavailable
and the first one will have the ownership
"""


@pytest_asyncio.fixture
async def db_properties(
    async_session: AsyncSession, db_staff_user: UserOutputSchema
) -> PagedResponseSchema[PropertyOutputSchema]:
    properties = [
        await create_property(async_session, property_input) for property_input in DB_PROPERTIES_SCHEMAS
    ]
    await change_property_owner(
        async_session, UserIdSchema(id=db_staff_user.id), properties[0].id
    )
    return await get_all_properties(async_session, PageParams())
