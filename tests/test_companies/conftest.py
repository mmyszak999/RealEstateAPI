import subprocess

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.apps.companies.schemas import CompanyOutputSchema, CompanyInputSchema
from src.apps.companies.services import create_company, add_single_user_to_company, get_all_companies
from src.core.factory.company_factory import (
    CompanyInputSchemaFactory
)
from src.apps.users.schemas import UserOutputSchema, UserIdSchema
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_users.conftest import db_user, db_staff_user

DB_COMPANIES_SCHEMAS = [CompanyInputSchemaFactory().generate() for _ in range(3)]


@pytest_asyncio.fixture
async def db_companies(
    async_session: AsyncSession,db_staff_user: UserOutputSchema
) -> PagedResponseSchema[CompanyOutputSchema]:
    companies = [
        await create_company(async_session, company_input) for company_input in DB_COMPANIES_SCHEMAS
    ]
    await add_single_user_to_company(
        async_session, UserIdSchema(id=db_staff_user.id), companies[0].id
    )
    return await get_all_companies(async_session, PageParams(), output_schema=CompanyOutputSchema)
