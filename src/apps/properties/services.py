from typing import Union

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.apps.properties.models import Property
from src.apps.properties.schemas import (
    PropertyInputSchema,
    PropertyOutputSchema,
    PropertyUpdateSchema,
    PropertyBasicOutputSchema,
    PropertyOwnerIdSchema
)
from src.apps.users.models import User
from src.apps.properties.enums import PropertyStatusEnum, PropertyTypeEnum
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied, 
    OwnerAlreadyHasTheOwnershipException,
    IncorrectEnumValueException,
    ServiceException
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists


async def create_property(
    session: AsyncSession, property_input: PropertyInputSchema
) -> PropertyBasicOutputSchema:
    property_data = property_input.dict()
    if owner_id := property_data.get("owner_id"):
        if not (owner_object := await if_exists(User, "id", owner_id, session)):
            raise DoesNotExist(User.__name__, "id", owner_id)
        
        if not owner_object.is_active:
            raise ServiceException("Inactive user cannot be assigned as a property owner! ")
        
    
    property_status = property_data.get('property_status', "").value
    if property_status and (property_status not in PropertyStatusEnum.list_values()):
        raise IncorrectEnumValueException(
            "property_status", property_status, PropertyStatusEnum.list_values()
        )
        
    property_type = property_data.get('property_type', "").value
    if property_type and (property_type not in PropertyTypeEnum.list_values()):
        raise IncorrectEnumValueException(
            "property_type", property_type, PropertyTypeEnum.list_values()
        )

    new_property = Property(**property_data)
    session.add(new_property)
    await session.commit()

    return PropertyBasicOutputSchema.from_orm(new_property)


async def get_single_property(
    session: AsyncSession, property_id: str, output_schema: BaseModel = PropertyOutputSchema
) -> Union[
        PropertyOutputSchema,
        PropertyBasicOutputSchema
        ]:
    if not (property_object := await if_exists(Property, "id", property_id, session)):
        raise DoesNotExist(Property.__name__, "id", property_id)

    return output_schema.from_orm(property_object)


async def get_all_properties(
    session: AsyncSession,
    page_params: PageParams,
    get_available: bool = False,
    get_rented: bool = False,
    output_schema: BaseModel = PropertyBasicOutputSchema,
    query_params: list[tuple] = None
) -> PagedResponseSchema[PropertyBasicOutputSchema]:
    query = select(Property)
    if get_available:
        query = query.filter(Property.property_status == PropertyStatusEnum.AVAILABLE)
        
    if get_rented:
        query = query.filter(Property.property_status == PropertyStatusEnum.RENTED)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Property)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=Property,
        page_params=page_params,
        session=session,
    )


async def update_single_property(
    session: AsyncSession, property_input: PropertyUpdateSchema, property_id: str
) -> PropertyOutputSchema:
    if not (property_object := await if_exists(Property, "id", property_id, session)):
        raise DoesNotExist(Property.__name__, "id", property_id)

    property_data = property_input.dict(exclude_unset=True, exclude_none=True)

    property_status = property_data.get('property_status', "")
    
    if property_status and (property_status not in PropertyStatusEnum.list_values()):
        raise IncorrectEnumValueException(
            "property_status", property_status, PropertyStatusEnum.list_values()    
        )
        
    property_type = property_data.get('property_type', "")
    
    if property_type and (property_type not in PropertyTypeEnum.list_values()):
        raise IncorrectEnumValueException(
            "property_type", property_type, PropertyTypeEnum.list_values()
        )

    if property_data:
        statement = (
                update(Property).filter(Property.id == property_id).values(**property_data)
            )
    
    await session.execute(statement)
    await session.commit()
    await session.refresh(property_object)

    return await get_single_property(session, property_id=property_id)


async def change_property_owner(
    session: AsyncSession, property_input: PropertyOwnerIdSchema, property_id: str
) -> None:
    if not (property_object := await if_exists(Property, "id", property_id, session)):
        raise DoesNotExist(Property.__name__, "id", property_id)

    property_data = property_input.dict()
    
    owner_id = property_data.get("id", "")

    if owner_id:
        owner_object = await if_exists(User, "id", owner_id, session)
        if not owner_object:
            raise DoesNotExist(User.__name__, "id", owner_id)
        
        if not owner_object.is_active:
            raise ServiceException("Inactive user cannot be the property owner! ")
        
        if property_object.owner_id == owner_object.id:
            raise OwnerAlreadyHasTheOwnershipException
    
    property_object.owner_id = owner_id
    session.add(property_object)
    await session.commit()
    await session.refresh(property_object)
    return
