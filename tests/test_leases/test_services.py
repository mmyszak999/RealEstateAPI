import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.apps.leases.schemas import LeaseOutputSchema
from src.apps.properties.schemas import PropertyOutputSchema

from src.apps.leases.services import (
    create_lease,
    get_all_leases,
    get_single_lease,
    update_single_lease,
    manage_lease_renewal_status
)
from src.apps.properties.services import create_property, update_single_property, get_all_properties
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    ServiceException,
    PropertyWithoutOwnerException,
    PropertyNotAvailableForRentException,
    UserCannotLeaseNotTheirPropertyException,
    UserCannotRentTheirPropertyForThemselvesException,
    ActiveLeaseException,
    IncorrectLeaseDatesException,
    CantModifyExpiredLeaseException,
    TenantAlreadyAcceptedRenewalException,
    TenantAlreadyDiscardedRenewalException
    )
from src.core.factory.lease_factory import (
    LeaseInputSchemaFactory,
    LeaseUpdateSchemaFactory,
)
from src.core.factory.property_factory import (
    PropertyInputSchemaFactory,
    PropertyUpdateSchemaFactory
)
from src.apps.leases.enums import BillingPeriodEnum
from src.apps.properties.enums import PropertyStatusEnum
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_leases.conftest import db_leases
from tests.test_properties.conftest import db_properties
from tests.test_addresses.conftest import db_addresses
from tests.test_companies.conftest import db_companies
from tests.test_users.conftest import db_staff_user, db_user, db_superuser
from src.core.utils.orm import if_exists
from src.apps.users.models import User
from src.apps.properties.models import Property
from src.apps.leases.models import Lease


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_requested_property_does_not_exist(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema
):
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=generate_uuid(),
        owner_id=db_staff_user.id,
        tenant_id=db_user.id
    )
    with pytest.raises(DoesNotExist):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_property_does_not_have_an_owner(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema
):
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.AVAILABLE,
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=db_staff_user.id,
        tenant_id=db_user.id
    )
    with pytest.raises(PropertyWithoutOwnerException):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_property_is_not_available(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema
):
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.UNAVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=db_staff_user.id,
        tenant_id=db_user.id
    )
    with pytest.raises(PropertyNotAvailableForRentException):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_requested_owner_does_not_exist(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema
):
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=generate_uuid(),
        tenant_id=db_user.id
    )
    with pytest.raises(DoesNotExist):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_requested_owner_is_not_the_property_owner(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema,
    db_superuser: UserOutputSchema
):
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=db_superuser.id,
        tenant_id=db_user.id
    )
    with pytest.raises(UserCannotLeaseNotTheirPropertyException):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_requested_owner_is_not_active(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema
):
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    owner = await if_exists(User, "id", db_staff_user.id, async_session)
    owner.is_active = False
    async_session.add(owner)
    await async_session.commit()
    await async_session.refresh(owner)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=db_staff_user.id,
        tenant_id=db_user.id
    )
    with pytest.raises(ServiceException):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_requested_tenant_does_not_exist(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema
):
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=db_staff_user.id,
        tenant_id=generate_uuid()
    )
    with pytest.raises(DoesNotExist):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_property_owner_is_the_requested_tenant(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema
):
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=db_staff_user.id,
        tenant_id=db_staff_user.id
    )
    with pytest.raises(UserCannotRentTheirPropertyForThemselvesException):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_requested_tenant_is_not_active(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema
):
    tenant = await if_exists(User, "id", db_user.id, async_session)
    tenant.is_active = False
    async_session.add(tenant)
    await async_session.commit()
    await async_session.refresh(tenant)
    
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=db_staff_user.id,
        tenant_id=db_user.id
    )
    with pytest.raises(ServiceException):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_lease_and_start_date_is_bigger_than_the_end_date(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema
):
    property_input = PropertyInputSchemaFactory().generate(
        
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        start_date=date.today() + timedelta(days=1),
        end_date=date.today(),
        property_id=property_output.id,
        owner_id=db_staff_user.id,
        tenant_id=db_user.id
    )
    with pytest.raises(IncorrectLeaseDatesException):
        await create_lease(async_session, lease_input)


@pytest.mark.asyncio
async def test_if_property_has_reserved_status_when_created_a_lease(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema,
    db_properties: PagedResponseSchema[PropertyOutputSchema]
):
    property_input = PropertyInputSchemaFactory().generate(
        
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=db_staff_user.id,
        tenant_id=db_user.id
    )
    lease_output = await create_lease(async_session, lease_input)
    lease_output = await get_single_lease(async_session, lease_output.id)
    
    assert lease_output.property.property_status == PropertyStatusEnum.RESERVED
    

@pytest.mark.asyncio
async def test_if_only_one_lease_was_returned(
    async_session: AsyncSession,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
):
    lease = await get_single_lease(async_session, db_leases.results[0].id)

    assert lease.id == db_leases.results[0].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_lease(
    async_session: AsyncSession,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_lease(async_session, generate_uuid())



@pytest.mark.asyncio
async def test_if_only_specific_leases_were_returned(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    db_user: UserOutputSchema,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    property_input = PropertyInputSchemaFactory().generate(
        property_status=PropertyStatusEnum.AVAILABLE,
        owner_id=db_staff_user.id
    )
    property_output = await create_property(async_session, property_input)
    
    lease_input = LeaseInputSchemaFactory().generate(
        property_id=property_output.id,
        owner_id=db_staff_user.id,
        tenant_id=db_user.id
    )
    lease_output = await create_lease(async_session, lease_input)
    
    #get all leases
    leases = await get_all_leases(async_session, PageParams())
    assert leases.total == db_leases.total + 1
    
    lease = await if_exists(Lease, "id", lease_output.id, async_session)
    lease.lease_expired = True
    async_session.add(lease)
    await async_session.commit()
    await async_session.refresh(lease)
    
    #only non-expired (active)
    leases = await get_all_leases(async_session, PageParams(), get_active=True)
    assert leases.total == 1
    
    #only expired
    leases = await get_all_leases(async_session, PageParams(), get_expired=True)
    assert leases.total == 1
    
    lease = await if_exists(Lease, "id", lease_output.id, async_session)
    lease.renewal_accepted = True
    async_session.add(lease)
    await async_session.commit()
    await async_session.refresh(lease)
    
    #with renewal accepted
    leases = await get_all_leases(async_session, PageParams(), get_with_renewal_accepted=True)
    assert leases.total == 1
    
    
@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_lease(
    async_session: AsyncSession,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
):
    update_data = LeaseUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_lease(async_session, update_data, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_updating_expired_lease(
    async_session: AsyncSession,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
):
    lease = await if_exists(Lease, "id", db_leases.results[0].id, async_session)
    lease.lease_expired = True
    async_session.add(lease)
    await async_session.commit()
    await async_session.refresh(lease)
    
    update_data = LeaseUpdateSchemaFactory().generate(rent_amount=1243)
    with pytest.raises(CantModifyExpiredLeaseException):
        await update_single_lease(async_session, update_data, lease.id)


@pytest.mark.asyncio
async def test_raise_exception_while_updating_lease_and_new_expiration_date_smaller_than_end_date(
    async_session: AsyncSession,
    db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    lease_output = db_leases.results[0]    
    update_data = LeaseUpdateSchemaFactory().generate(
        lease_expiration_date=lease_output.start_date-timedelta(days=4)
    )
    with pytest.raises(ServiceException):
        await update_single_lease(async_session, update_data, lease_output.id)


@pytest.mark.asyncio
async def test_check_if_lease_dates_are_updated_correctly_when_changing_lease_expiration_date(
    async_session: AsyncSession,
    db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    lease_output = db_leases.results[0]
    new_lease_expiration_date = date(2027, 12, 2)
    update_data = LeaseUpdateSchemaFactory().generate(
        lease_expiration_date=new_lease_expiration_date
    )
    updated_lease = await update_single_lease(async_session, update_data, lease_output.id)
    lease_output = await get_single_lease(async_session, updated_lease.id)
    assert lease_output.lease_expiration_date == lease_output.end_date == new_lease_expiration_date
    
    
@pytest.mark.asyncio
async def test_raise_exception_while_managing_renewal_status_of_nonexistent_lease(
    async_session: AsyncSession,
    db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    with pytest.raises(DoesNotExist):
        await manage_lease_renewal_status(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_attempting_to_accept_accepted_lease_renewal(
    async_session: AsyncSession,
    db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    lease = await if_exists(Lease, "id", db_leases.results[0].id, async_session)
    lease.renewal_accepted = True
    async_session.add(lease)
    await async_session.commit()
    await async_session.refresh(lease)
    
    with pytest.raises(TenantAlreadyAcceptedRenewalException):
        await manage_lease_renewal_status(async_session, lease.id)


@pytest.mark.asyncio
async def test_raise_exception_when_attempting_to_discard_discarded_lease_renewal(
    async_session: AsyncSession,
    db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    with pytest.raises(TenantAlreadyDiscardedRenewalException):
        await manage_lease_renewal_status(async_session, db_leases.results[0].id, accept_renewal=False)