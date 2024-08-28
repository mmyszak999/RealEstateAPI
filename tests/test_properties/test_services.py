import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.apps.properties.schemas import PropertyOutputSchema, PropertyOwnerIdSchema
from src.apps.properties.services import (
    create_property,
    get_all_properties,
    get_single_property,
    update_single_property,
    change_property_owner
)
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    ServiceException,
    IncorrectEnumValueException,
    OwnerAlreadyHasTheOwnershipException
    )
from src.core.factory.property_factory import (
    PropertyInputSchemaFactory,
    PropertyUpdateSchemaFactory,
)
from src.apps.properties.enums import PropertyStatusEnum, PropertyTypeEnum
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_properties.conftest import DB_PROPERTIES_SCHEMAS, db_properties
from tests.test_users.conftest import db_staff_user, db_user
from src.core.utils.orm import if_exists
from src.apps.users.models import User


@pytest.mark.asyncio
async def test_raise_exception_when_creating_property_and_owner_does_not_exists(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
):
    schema = PropertyInputSchemaFactory().generate(owner_id=generate_uuid())
    with pytest.raises(DoesNotExist):
        await create_property(async_session, schema)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_property_and_owner_is_not_active(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_user: UserOutputSchema
):
    user = await if_exists(User, "id", db_user.id, async_session)
    user.is_active = False
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    schema = PropertyInputSchemaFactory().generate(owner_id=user.id)
    with pytest.raises(ServiceException):
        await create_property(async_session, schema)

@pytest.mark.asyncio
async def test_if_only_one_property_was_returned(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
):
    property = await get_single_property(async_session, db_properties.results[1].id)

    assert property.id == db_properties.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_property(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_property(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_only_available_properties_were_returned(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
):
    properties = await get_all_properties(async_session, PageParams(page=1, size=5), get_available=True)
    assert properties.total == db_properties.total - 1


@pytest.mark.asyncio
async def test_if_all_properties_were_returned(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
):
    properties = await get_all_properties(async_session, PageParams(page=1, size=5))
    assert properties.total == db_properties.total


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_property(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
):
    update_data = PropertyUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_property(async_session, update_data, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_updating_property_and_entered_incorrect_property_status(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_user: UserOutputSchema
):
    schema = PropertyUpdateSchemaFactory().generate()
    schema.property_status = "no_such_status"
    with pytest.raises(IncorrectEnumValueException):
        await update_single_property(async_session, schema, db_properties.results[0].id)


@pytest.mark.asyncio
async def test_raise_exception_when_updating_property_and_entered_incorrect_property_type(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_user: UserOutputSchema
):
    schema = PropertyUpdateSchemaFactory().generate()
    schema.property_type = "no_such_type"
    with pytest.raises(IncorrectEnumValueException):
        await update_single_property(async_session, schema, db_properties.results[0].id)
        
        
@pytest.mark.asyncio
async def test_raise_exception_when_changing_owner_of_nonexistent_property(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_user: UserOutputSchema
):
    schema = PropertyOwnerIdSchema(id=db_user.id)
    with pytest.raises(DoesNotExist):
        await change_property_owner(async_session, schema, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_changing_the_property_ownership_and_owner_does_not_exist(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_user: UserOutputSchema
):
    schema = PropertyOwnerIdSchema(id=generate_uuid())
    with pytest.raises(DoesNotExist):
        await change_property_owner(async_session, schema, db_properties.results[1].id)


@pytest.mark.asyncio
async def test_raise_exception_when_changing_owner_of_nonexistent_property_and_owner_is_not_active(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_user: UserOutputSchema
):
    user = await if_exists(User, "id", db_user.id, async_session)
    user.is_active = False
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    schema = PropertyOwnerIdSchema(id=user.id)
    with pytest.raises(DoesNotExist):
        await change_property_owner(async_session, schema, db_properties.results[1].id)


@pytest.mark.asyncio
async def test_raise_exception_when_changing_owner_of_nonexistent_property_and_owner_is_not_active(
    async_session: AsyncSession,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_user: UserOutputSchema
):
    schema = PropertyOwnerIdSchema(id=db_user.id)
    await change_property_owner(async_session, schema, db_properties.results[1].id)
    
    with pytest.raises(OwnerAlreadyHasTheOwnershipException):
        await change_property_owner(async_session, schema, db_properties.results[1].id)