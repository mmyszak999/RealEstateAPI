from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.properties.models import Property
from src.apps.properties.schemas import (
    PropertyInputSchema,
    PropertyOutputSchema,
    PropertyUpdateSchema,
    PropertyBasicOutputSchema
)
from src.apps.users.models import User
from src.apps.properties.enums import PropertyStatusEnum, PropertyTypeEnum
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied, 
    OwnerAlreadyHasTheOwnershipException,
    IncorrectEnumValueException
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists


async def create_property(
    session: AsyncSession, property_input: PropertyInputSchema
) -> PropertyOutputSchema:
    property_data = property_input.dict()
    if owner_id := property_data.get("owner_id"):
        if not (owner_object := await if_exists(User, "id", owner_id, session)):
            raise DoesNotExist(User.__name__, "id", owner_id)
    
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

    new_property = Property(**property_data)
    session.add(new_property)
    await session.commit()

    return PropertyOutputSchema.from_orm(new_property)


async def get_single_property(
    session: AsyncSession, property_id: int
) -> PropertyOutputSchema:
    if not (property_object := await if_exists(Property, "id", property_id, session)):
        raise DoesNotExist(Property.__name__, "id", property_id)

    return PropertyOutputSchema.from_orm(property_object)


async def get_all_properties(
    session: AsyncSession,
    page_params: PageParams,
    get_available: bool = False,
    get_rented: bool = False,
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
        response_schema=PropertyBasicOutputSchema,
        table=Property,
        page_params=page_params,
        session=session,
    )


async def update_single_property(
    session: AsyncSession, property_input: PropertyUpdateSchema, property_id: int
) -> PropertyOutputSchema:
    if not (property_object := await if_exists(Property, "id", property_id, session)):
        raise DoesNotExist(Property.__name__, "id", property_id)

    property_data = property_input.dict(exclude_unset=True, exclude_none=True)
    
    owner_id = property_data.get("owner_id")

    if owner_id:
        owner_object = await if_exists(User, "id", owner_id, session)
        if not owner_object:
            raise DoesNotExist(User.__name__, "id", owner_id)
        
        if property_object.owner_id == owner_object.id:
            raise OwnerAlreadyHasTheOwnershipException
    

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


async def delete_single_property(session: AsyncSession):
    
    statement = delete(Property)
    result = await session.execute(statement)
    await session.commit()

    return result
