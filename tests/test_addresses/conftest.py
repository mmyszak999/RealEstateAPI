import subprocess

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.apps.addresses.schemas import AddressOutputSchema, AddressInputSchema
from src.apps.addresses.services import create_address, add_single_user_to_address, get_all_addresses
from src.core.factory.address_factory import (
    AddressInputSchemaFactory
)
from src.apps.users.schemas import UserOutputSchema, UserIdSchema
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_users.conftest import db_user, db_staff_user

DB_ADDRESSES_SCHEMAS = [AddressInputSchemaFactory().generate() for _ in range(2)]
#the last schema is not used


@pytest_asyncio.fixture
async def db_addresses(
    async_session: AsyncSession
) -> PagedResponseSchema[AddressOutputSchema]:
    addresses = [
        await create_address(async_session, address_input) for address_input in DB_ADDRESSES_SCHEMAS
    ]
    await add_single_user_to_address(
        async_session, UserIdSchema(id=db_staff_user.id), addresses[0].id
    )
    return await get_all_addresses(async_session, PageParams())
