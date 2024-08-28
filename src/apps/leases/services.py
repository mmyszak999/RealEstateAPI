from typing import Union

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
    PropertyNotAvailableForRentException
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
        
        if property_object.property_status != PropertyStatusEnum.AVAILABLE:
            raise PropertyNotAvailableForRentException
    
    if owner_id := lease_data.get("owner_id"):
        if not (owner_object := await if_exists(User, "id", owner_id, session)):
            raise DoesNotExist(User.__name__, "id", owner_id)
        
        if not owner_object.is_active:
            raise ServiceException("Inactive user cannot be assigned as a lease owner! ")
        
        if not owner_object
    
    lease_status = lease_data.get('lease_status', "").value
    if lease_status and (lease_status not in LeaseStatusEnum.list_values()):
        raise IncorrectEnumValueException(
            "lease_status", lease_status, LeaseStatusEnum.list_values()
        )
        
    lease_type = lease_data.get('lease_type', "").value
    if lease_type and (lease_type not in LeaseTypeEnum.list_values()):
        raise IncorrectEnumValueException(
            "lease_type", lease_type, LeaseTypeEnum.list_values()
        )

    new_lease = Lease(**lease_data)
    session.add(new_lease)
    await session.commit()

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
    get_available: bool = False,
    get_rented: bool = False,
    output_schema: BaseModel = LeaseBasicOutputSchema,
    query_params: list[tuple] = None
) -> PagedResponseSchema[LeaseBasicOutputSchema]:
    query = select(Lease)
    if get_available:
        query = query.filter(Lease.lease_status == LeaseStatusEnum.AVAILABLE)
        
    if get_rented:
        query = query.filter(Lease.lease_status == LeaseStatusEnum.RENTED)

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
) -> LeaseOutputSchema:
    if not (lease_object := await if_exists(Lease, "id", lease_id, session)):
        raise DoesNotExist(Lease.__name__, "id", lease_id)

    lease_data = lease_input.dict(exclude_unset=True, exclude_none=True)

    lease_status = lease_data.get('lease_status', "")
    
    if lease_status and (lease_status not in LeaseStatusEnum.list_values()):
        raise IncorrectEnumValueException(
            "lease_status", lease_status, LeaseStatusEnum.list_values()    
        )
        
    lease_type = lease_data.get('lease_type', "")
    
    if lease_type and (lease_type not in LeaseTypeEnum.list_values()):
        raise IncorrectEnumValueException(
            "lease_type", lease_type, LeaseTypeEnum.list_values()
        )

    if lease_data:
        statement = (
                update(Lease).filter(Lease.id == lease_id).values(**lease_data)
            )
    
    await session.execute(statement)
    await session.commit()
    await session.refresh(lease_object)

    return await get_single_lease(session, lease_id=lease_id)


async def change_lease_owner(
    session: AsyncSession, lease_input: LeaseOwnerIdSchema, lease_id: str
) -> None:
    if not (lease_object := await if_exists(Lease, "id", lease_id, session)):
        raise DoesNotExist(Lease.__name__, "id", lease_id)

    lease_data = lease_input.dict()
    
    owner_id = lease_data.get("id", "")

    if owner_id:
        owner_object = await if_exists(User, "id", owner_id, session)
        if not owner_object:
            raise DoesNotExist(User.__name__, "id", owner_id)
        
        if not owner_object.is_active:
            raise ServiceException("Inactive user cannot be the lease owner! ")
        
        if lease_object.owner_id == owner_object.id:
            raise OwnerAlreadyHasTheOwnershipException
    
    lease_object.owner_id = owner_id
    session.add(lease_object)
    await session.commit()
    await session.refresh(lease_object)
    return
