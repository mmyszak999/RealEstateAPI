from typing import Union
from datetime import date, datetime, timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.apps.leases.models import Lease
from src.apps.leases.schemas import (
    LeaseInputSchema,
    LeaseOutputSchema,
    LeaseUpdateSchema,
    LeaseBasicOutputSchema
)
from src.apps.properties.models import Property
from src.apps.properties.enums import PropertyStatusEnum
from src.apps.users.models import User
from src.apps.leases.enums import BillingPeriodEnum
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied, 
    IncorrectEnumValueException,
    ServiceException,
    PropertyNotAvailableForRentException,
    UserCannotLeaseNotTheirPropertyException,
    ActiveLeaseException,
    IncorrectLeaseDatesException,
    CantModifyExpiredLeaseException,
    TenantAlreadyAcceptedRenewalException,
    TenantAlreadyDiscardedRenewalException,
    PropertyWithoutOwnerException
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists


async def create_lease(
    session: AsyncSession, lease_input: LeaseInputSchema
) -> LeaseBasicOutputSchema:
    lease_data = lease_input.dict()
    if property_id := lease_data.get("property_id"):
        if not (property_object := await if_exists(Property, "id", property_id, session)):
            raise DoesNotExist(Property.__name__, "id", property_id)
        
        if not property_object.owner:
            raise PropertyWithoutOwnerException
        
        if property_object.property_status != PropertyStatusEnum.AVAILABLE:
            raise PropertyNotAvailableForRentException
    
    if owner_id := lease_data.get("owner_id"):
        if not (owner_object := await if_exists(User, "id", owner_id, session)):
            raise DoesNotExist(User.__name__, "id", owner_id)
        
        if property_object.owner_id != owner_id:
            raise UserCannotLeaseNotTheirPropertyException
        
        if not owner_object.is_active:
            raise ServiceException("Inactive user cannot be assigned as a lease owner! ")
    
    
    if tenant_id := lease_data.get("tenant_id"):
        if not (tenant_object := await if_exists(User, "id", tenant_id, session)):
            raise DoesNotExist(User.__name__, "id", tenant_id)
        
        if tenant_id == owner_id:
            raise ServiceException("Tenant id and owner id have to be different! ")
        
        if not tenant_object.is_active:
            raise ServiceException("Inactive user cannot be assigned as a tenant! ")
    
    statement = select(Lease
            ).where(
                Lease.property_id == property_id,
                Lease.lease_expired == False,
                Lease.lease_expiration_date >= lease_data.get("start_date")
        )
    active_property_lease_check = await session.scalars(statement)
    
    if active_property_lease_check.unique().all():
        raise ActiveLeaseException
    
    start_date, end_date = lease_data.get("start_date"), lease_data.get("end_date")
    if (start_date and end_date) and (start_date > end_date):
        raise IncorrectLeaseDatesException(end_date, start_date)
    
    billing_period = lease_data.get('billing_period', "").value
    if billing_period and (billing_period not in BillingPeriodEnum.list_values()):
        raise IncorrectEnumValueException(
            "billing_period", billing_period, BillingPeriodEnum.list_values()
        )

    new_lease = Lease(**lease_data)
    session.add(new_lease)
    property_object.property_status = PropertyStatusEnum.RESERVED
    session.add(property_object)
    await session.commit()
    await session.refresh(new_lease)
    await session.refresh(property_object)

    return LeaseBasicOutputSchema.from_orm(new_lease)


async def get_single_lease(
    session: AsyncSession, lease_id: str, output_schema: BaseModel = LeaseOutputSchema
) -> Union[
        LeaseOutputSchema,
        LeaseBasicOutputSchema
        ]:
    if not (lease_object := await if_exists(Lease, "id", lease_id, session)):
        raise DoesNotExist(Lease.__name__, "id", lease_id)

    return output_schema.from_orm(lease_object)


async def get_all_leases(
    session: AsyncSession,
    page_params: PageParams,
    get_with_renewal_accepted: bool = False,
    get_expired: bool = False,
    get_active: bool = False,
    output_schema: BaseModel = LeaseBasicOutputSchema,
    query_params: list[tuple] = None
) -> PagedResponseSchema[LeaseBasicOutputSchema]:
    query = select(Lease)
    if get_with_renewal_accepted:
        query = query.filter(Lease.renewal_accepted == True)
        
    if get_expired:
        query = query.filter(Lease.lease_expired == True)
        
    if get_active:
        query = query.filter(Lease.lease_expired == False)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Lease)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=Lease,
        page_params=page_params,
        session=session,
    )


async def update_single_lease(
    session: AsyncSession, lease_input: LeaseUpdateSchema, lease_id: str
) -> LeaseBasicOutputSchema:
    if not (lease_object := await if_exists(Lease, "id", lease_id, session)):
        raise DoesNotExist(Lease.__name__, "id", lease_id)

    lease_data = lease_input.dict(exclude_unset=True, exclude_none=True)
    
    if lease_object.lease_expired:
        raise CantModifyExpiredLeaseException
    
    lease_expiration_date = lease_data.get('lease_expiration_date')
    end_date = lease_object.end_date or None
    
    if lease_expiration_date:
        if lease_expiration_date < date.today() < lease_object.start_date:
            raise ServiceException(
                "Expiration date cannot be smaller than the lease start date and the current date! "
            )
        if end_date != None:
            lease_object.end_date = lease_expiration_date
        lease_object.lease_expiration_date = lease_expiration_date
        session.add(lease_object)
    
    if lease_data:
        statement = (
                update(Lease).filter(Lease.id == lease_id).values(**lease_data)
            )
    
        await session.execute(statement)
        await session.commit()
        await session.refresh(lease_object)

    return await get_single_lease(session, lease_id=lease_id, output_schema=LeaseBasicOutputSchema)



async def manage_lease_renewal_status(
    session: AsyncSession, lease_id: str, accept_renewal: bool = True
) -> None:
    if not (lease_object := await if_exists(Lease, "id", lease_id, session)):
        raise DoesNotExist(Lease.__name__, "id", lease_id)

    if lease_object.renewal_accepted and accept_renewal:
        raise TenantAlreadyAcceptedRenewalException
    
    if (not lease_object.renewal_accepted and not accept_renewal):
        raise TenantAlreadyDiscardedRenewalException
    
    lease_object.renewal_accepted = accept_renewal
    session.add(lease_object)
    await session.commit()
    await session.refresh(lease_object)
    return


async def accept_single_lease_renewal(
    session: AsyncSession, lease_id: str,
) -> None:
    return await manage_lease_renewal_status(
        session, lease_id
    )


async def discard_single_lease_renewal(
    session: AsyncSession, lease_id: str,
) -> None:
    return await manage_lease_renewal_status(
        session, lease_id, accept_renewal=False
    )



async def base_manage_lease_renewals_and_expired_statuses(
    session: AsyncSession, lease: Lease
) -> None:
    lease.lease_expired = True
    if lease.renewal_accepted:
        lease_input = LeaseInputSchema.from_orm(lease)
        old_start_date = lease_input.start_date
        old_end_date = lease_input.end_date

        date_difference = old_end_date - old_start_date
        lease_input.start_date = date.today()
        lease_input.end_date = lease_input.start_date + date_difference
        
        new_lease = Lease(**lease_input.dict())
        session.add(new_lease)
        await session.flush()
        new_lease.property.property_status = PropertyStatusEnum.RENTED
        session.add(new_lease)
    lease.property.property_status = PropertyStatusEnum.AVAILABLE
    session.add(lease)
    
    
async def manage_lease_renewals_and_expired_statuses(
    session: AsyncSession
) -> None:
    statement = select(Lease).filter(
        Lease.lease_expired == False,
        Lease.lease_expiration_date > date.today()
    )
    expired_leases = session.scalars(statement).unique().all()
    [
        await (base_manage_lease_renewals_and_expired_statuses(session, lease))
        for lease in expired_leases
    ]
    await session.commit()


async def base_manage_property_statuses_for_lease_with_the_start_date_being_today(
    session: AsyncSession, lease: Lease
) -> None:
    lease.property.property_status == PropertyStatusEnum.RENTED
    session.add(lease)
    

async def manage_property_statuses_for_lease_with_the_start_date_being_today(
    session: AsyncSession
) -> None:
    statement = select(Lease).filter(
        Lease.lease_expired == False,
        Lease.start_date == date.today()
    )
    leases_with_the_first_day = session.scalars(statement).unique().all()
    [
        await (base_manage_property_statuses_for_lease_with_the_start_date_being_today(session, lease))
        for lease in leases_with_the_first_day
    ]
    await session.commit()



"""
task który będzie sprawdzał lease gdzie lease_expired=False
    jak lease expired == False a expiration date większa niż date.today()
    to wtedy daje lease_expired=True
    ponadto patrzę czy jest renewal_accepted=True
    jak tak to tworzę lease na tych samych warunkach
    ale modyfikuje start date i end date
    jak nie to wtedy daję property_status na available
    
jak jest tworzone lease, to property jest RESERVED,
jak nastepuje start date to wtedy jest RENTED
potem jak wygasa umowa to staje sie AVAILABLE
"""