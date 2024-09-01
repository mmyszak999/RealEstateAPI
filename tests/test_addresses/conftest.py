import subprocess

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.apps.addresses.schemas import AddressInputSchema, AddressOutputSchema
from src.apps.addresses.services import create_address, get_all_addresses
from src.apps.companies.schemas import CompanyOutputSchema
from src.apps.properties.schemas import PropertyOutputSchema
from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.core.factory.address_factory import AddressInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_companies.conftest import db_companies
from tests.test_properties.conftest import db_properties
from tests.test_users.conftest import db_staff_user, db_user

DB_COMPANIES_ADDRESSES_SCHEMAS = [
    AddressInputSchemaFactory().generate() for _ in range(2)
]
DB_PROPERTIES_ADDRESSES_SCHEMAS = [
    AddressInputSchemaFactory().generate() for _ in range(3)
]

"""
    every company and 2 properties out of 3 got address
"""


@pytest_asyncio.fixture
async def db_addresses(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    db_properties: PagedResponseSchema[PropertyOutputSchema],
) -> PagedResponseSchema[AddressOutputSchema]:
    for address_input, company in zip(
        DB_COMPANIES_ADDRESSES_SCHEMAS, db_companies.results[:-1]
    ):
        address_input.company_id = company.id
        await create_address(async_session, address_input)

    for address_input, property in zip(
        DB_PROPERTIES_ADDRESSES_SCHEMAS, db_properties.results[:-1]
    ):
        address_input.property_id = property.id
        await create_address(async_session, address_input)

    return await get_all_addresses(async_session, PageParams())
