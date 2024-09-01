import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.companies.schemas import CompanyOutputSchema
from src.apps.companies.services import (
    add_single_user_to_company,
    create_company,
    get_all_companies,
    get_single_company,
    manage_user_company_status,
    remove_single_user_from_company,
    update_single_company,
)
from src.apps.users.models import User
from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    ServiceException,
    UserAlreadyHasCompanyException,
    UserHasNoCompanyException,
)
from src.core.factory.company_factory import (
    CompanyInputSchemaFactory,
    CompanyUpdateSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_companies.conftest import DB_COMPANIES_SCHEMAS, db_companies
from tests.test_users.conftest import db_staff_user, db_user


@pytest.mark.asyncio
async def test_raise_exception_when_creating_company_that_already_exists(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
):
    with pytest.raises(AlreadyExists):
        await create_company(async_session, DB_COMPANIES_SCHEMAS[0])


@pytest.mark.asyncio
async def test_if_only_one_company_was_returned(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
):
    company = await get_single_company(async_session, db_companies.results[1].id)

    assert company.id == db_companies.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_company(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_company(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_companies_were_returned(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
):
    companies = await get_all_companies(async_session, PageParams(page=1, size=5))
    assert companies.total == db_companies.total


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_company(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
):
    update_data = CompanyUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_company(async_session, update_data, generate_uuid())


@pytest.mark.asyncio
async def test_if_company_can_have_occupied_name(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
):
    company_data = CompanyUpdateSchemaFactory().generate(
        company_name=db_companies.results[0].company_name
    )
    with pytest.raises(IsOccupied):
        await update_single_company(
            async_session, company_data, db_companies.results[1].id
        )


@pytest.mark.asyncio
async def test_raise_exception_when_managing_user_company_status_and_company_does_not_exist(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    db_staff_user: UserOutputSchema,
):
    schema = UserIdSchema(id=db_staff_user.id)
    with pytest.raises(DoesNotExist):
        await manage_user_company_status(async_session, schema, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_managing_user_company_status_and_user_does_not_exist(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    db_staff_user: UserOutputSchema,
):
    schema = UserIdSchema(id=generate_uuid())
    with pytest.raises(DoesNotExist):
        await manage_user_company_status(
            async_session, schema, company_id=db_companies.results[0].id
        )


@pytest.mark.asyncio
async def test_raise_exception_when_managing_user_company_status_and_user_is_not_active(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema,
):
    user = await if_exists(User, "id", db_user.id, async_session)
    user.is_active = False
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    schema = UserIdSchema(id=user.id)
    with pytest.raises(ServiceException):
        await manage_user_company_status(
            async_session, schema, company_id=db_companies.results[0].id
        )


@pytest.mark.asyncio
async def test_raise_exception_when_managing_user_company_status_and_user_get_assigned_another_company(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema,
):
    schema = UserIdSchema(id=db_staff_user.id)
    with pytest.raises(UserAlreadyHasCompanyException):
        await add_single_user_to_company(
            async_session, schema, company_id=db_companies.results[0].id
        )


@pytest.mark.asyncio
async def test_raise_exception_when_managing_user_company_status_and_user_with_no_company_get_removed_from_one(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema,
):
    schema = UserIdSchema(id=db_user.id)
    with pytest.raises(UserHasNoCompanyException):
        await remove_single_user_from_company(
            async_session, schema, company_id=db_companies.results[0].id
        )
