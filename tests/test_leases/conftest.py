import subprocess

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.apps.leases.enums import BillingPeriodEnum
from src.apps.leases.schemas import LeaseInputSchema, LeaseOutputSchema
from src.apps.leases.services import create_lease, get_all_leases
from src.apps.properties.schemas import PropertyOutputSchema
from src.apps.properties.services import get_all_properties
from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.core.factory.lease_factory import LeaseInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_addresses.conftest import db_addresses
from tests.test_companies.conftest import db_companies
from tests.test_properties.conftest import db_properties
from tests.test_users.conftest import db_staff_user, db_superuser, db_user

"""
one lease exists
property owner -> db_staff_user
tenant -> db_superuser
"""


@pytest_asyncio.fixture
async def db_leases(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema,
    db_superuser: UserOutputSchema,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
) -> PagedResponseSchema[LeaseOutputSchema]:
    available_properties = await get_all_properties(
        async_session,
        PageParams(),
        get_available=True,
        output_schema=PropertyOutputSchema,
    )
    staff_property = [
        property
        for property in available_properties.results
        if property.owner_id == db_staff_user.id
    ]
    owner = staff_property[0].owner
    tenant = db_superuser
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=staff_property[0].id,
        owner_id=owner.id,
        tenant_id=tenant.id,
        billing_period=BillingPeriodEnum.MONTHLY,
    )
    await create_lease(async_session, lease_input)

    return await get_all_leases(
        async_session, PageParams(), output_schema=LeaseOutputSchema
    )
