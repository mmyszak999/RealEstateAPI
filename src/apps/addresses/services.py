from typing import Union

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.apps.addresses.models import Address
from src.apps.addresses.schemas import (
    AddressInputSchema,
    AddressOutputSchema,
    AddressUpdateSchema,
    AddressBasicOutputSchema
)
from src.apps.users.schemas import UserIdSchema
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    ServiceException,
    IncorrectCompanyOrPropertyValueException
)
from src.apps.companies.models import Company
from src.apps.properties.models import Property
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists
from src.apps.users.models import User


async def create_address(
    session: AsyncSession, address_input: AddressInputSchema
) -> AddressOutputSchema:
    address_data = address_input.dict()

    company_id = address_data.get("company_id")
    property_id = address_data.get("property_id")

    if bool(company_id) == bool(property_id):
        raise IncorrectCompanyOrPropertyValueException
    
    if company_id and (not (company_object := await if_exists(Company, "id", company_id, session))):
        raise DoesNotExist(Company.__name__, "id", company_id)
    
    if property_id and (not (property_object := await if_exists(Property, "id", property_id, session))):
        raise DoesNotExist(Property.__name__, "id", property_id)

    new_address = Address(**address_data)
    new_address.company_id = company_id
    new_address.property_id = property_id
    session.add(new_address)
    await session.commit()

    return AddressOutputSchema.from_orm(new_address)


async def get_single_address(
    session: AsyncSession, address_id: str, output_schema: BaseModel = AddressOutputSchema
) -> Union[
    AddressBasicOutputSchema,
    AddressOutputSchema
]:
    if not (address_object := await if_exists(Address, "id", address_id, session)):
        raise DoesNotExist(Address.__name__, "id", address_id)

    return output_schema.from_orm(address_object)


async def get_all_addresses(
    session: AsyncSession, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[AddressBasicOutputSchema]:
    query = select(Address)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Address)

    return await paginate(
        query=query,
        response_schema=AddressBasicOutputSchema,
        table=Address,
        page_params=page_params,
        session=session,
    )


async def update_single_address(
    session: AsyncSession, address_input: AddressUpdateSchema, address_id: str
) -> AddressBasicOutputSchema:
    if not (address_object := await if_exists(Address, "id", address_id, session)):
        raise DoesNotExist(Address.__name__, "id", address_id)

    address_data = address_input.dict(exclude_unset=True)

    if address_data:
        statement = (
            update(Address).filter(Address.id == address_id).values(**address_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(address_object)

    return await get_single_address(session, address_id=address_id, output_schema=AddressBasicOutputSchema)


async def add_single_user_to_address(
    session: AsyncSession, user_address_schema: UserIdSchema, address_id: str
) -> AddressOutputSchema:
    if not (address_object := await if_exists(Address, "id", address_id, session)):
        raise DoesNotExist(Address.__name__, "id", address_id)
    
    user_id = user_address_schema.id
    if not (user_object := await if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)
    
    if user_object.address:
        raise UserAlreadyHasAddressException
    
    if not user_object.is_active:
        raise ServiceException("Inactive user cannot be added to the address! ")
    
    user_object.address_id = address_id
    session.add(user_object)
    await session.commit()
    return
    
    
        
    
    