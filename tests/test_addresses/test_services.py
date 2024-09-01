import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.addresses.schemas import AddressOutputSchema
from src.apps.addresses.services import (
    create_address,
    get_all_addresses,
    get_single_address,
    update_single_address,
)
from src.apps.companies.models import Company
from src.apps.companies.schemas import CompanyOutputSchema
from src.apps.companies.services import get_all_companies, get_single_company
from src.apps.properties.models import Property
from src.apps.properties.schemas import PropertyOutputSchema
from src.apps.properties.services import get_all_properties, get_single_property
from src.apps.users.models import User
from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.core.exceptions import (
    AddressAlreadyAssignedException,
    AlreadyExists,
    DoesNotExist,
    IncorrectCompanyOrPropertyValueException,
    IsOccupied,
    ServiceException,
)
from src.core.factory.address_factory import (
    AddressInputSchemaFactory,
    AddressUpdateSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_addresses.conftest import (
    DB_COMPANIES_ADDRESSES_SCHEMAS,
    DB_PROPERTIES_ADDRESSES_SCHEMAS,
    db_addresses,
)
from tests.test_companies.conftest import db_companies
from tests.test_properties.conftest import db_properties
from tests.test_users.conftest import db_staff_user, db_superuser, db_user


@pytest.mark.asyncio
async def test_raise_exception_when_company_id_and_property_id_used_incorrectly_in_creating_address(
    async_session: AsyncSession,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_addresses: PagedResponseSchema[AddressOutputSchema],
):
    schema_1 = AddressInputSchemaFactory().generate()
    schema_2 = AddressInputSchemaFactory().generate(
        company_id=db_companies.results[-1].id, property_id=db_properties.results[-1].id
    )
    with pytest.raises(IncorrectCompanyOrPropertyValueException):
        await create_address(async_session, schema_1)
        await create_address(async_session, schema_2)


@pytest.mark.asyncio
async def test_raise_exception_while_creating_address_for_nonexistent_company(
    async_session: AsyncSession,
):
    schema = AddressInputSchemaFactory().generate(company_id=generate_uuid())
    with pytest.raises(DoesNotExist):
        await create_address(async_session, schema)


@pytest.mark.asyncio
async def test_raise_exception_while_creating_address_for_nonexistent_property(
    async_session: AsyncSession,
):
    schema = AddressInputSchemaFactory().generate(property_id=generate_uuid())
    with pytest.raises(DoesNotExist):
        await create_address(async_session, schema)


@pytest.mark.asyncio
async def test_raise_exception_when_company_or_property_already_have_address_assigned_when_creating_one(
    async_session: AsyncSession, db_addresses: PagedResponseSchema[AddressOutputSchema]
):
    all_companies = await get_all_companies(
        async_session, PageParams(), output_schema=CompanyOutputSchema
    )
    all_properties = await get_all_properties(
        async_session, PageParams(), output_schema=PropertyOutputSchema
    )

    companies_with_addresses = [
        company for company in all_companies.results if company.address
    ]
    properties_with_addresses = [
        property for property in all_properties.results if property.address
    ]

    schema_1 = AddressInputSchemaFactory().generate(
        company_id=companies_with_addresses[0].id,
    )
    schema_2 = AddressInputSchemaFactory().generate(
        property_id=properties_with_addresses[0].id
    )
    with pytest.raises(AddressAlreadyAssignedException):
        await create_address(async_session, schema_1)
        await create_address(async_session, schema_2)


@pytest.mark.asyncio
async def test_if_only_one_address_was_returned(
    async_session: AsyncSession,
    db_addresses: PagedResponseSchema[AddressOutputSchema],
):
    address = await get_single_address(async_session, db_addresses.results[1].id)

    assert address.id == db_addresses.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_address(
    async_session: AsyncSession,
    db_addresses: PagedResponseSchema[AddressOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_address(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_addresses_were_returned(
    async_session: AsyncSession,
    db_addresses: PagedResponseSchema[AddressOutputSchema],
):
    addresses = await get_all_addresses(async_session, PageParams(page=1, size=5))
    assert addresses.total == db_addresses.total


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_address(
    async_session: AsyncSession,
    db_addresses: PagedResponseSchema[AddressOutputSchema],
):
    update_data = AddressUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_address(async_session, update_data, generate_uuid())
