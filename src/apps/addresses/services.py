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
    IncorrectCompanyOrPropertyValueException,
    AddressAlreadyAssignedException
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
    """
        single address can be created for company or property object
        but not for both or none of them
    """
    company_object = None
    property_object = None

    address_data = address_input.dict()

    company_id = address_data.get("company_id")
    property_id = address_data.get("property_id")

    if bool(company_id) == bool(property_id):
        raise IncorrectCompanyOrPropertyValueException

    if company_id:
        if not (company_object := await if_exists(Company, "id", company_id, session)):
            raise DoesNotExist(Company.__name__, "id", company_id)
        if company_object.address is not None:
            raise AddressAlreadyAssignedException(object="Company")

    if property_id:
        if not (property_object := await if_exists(Property, "id", property_id, session)):
            raise DoesNotExist(Property.__name__, "id", property_id)
        if property_object and property_object.address is not None:
            raise AddressAlreadyAssignedException(object="Property")
 
    new_address = Address(**address_data)
    new_address.company_id = company_id
    new_address.property_id = property_id
    session.add(new_address)
    await session.commit()
    await session.refresh(new_address)

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

    address_data = address_input.dict(exclude_unset=True, exclude_none=True)

    if address_data:
        statement = (
            update(Address).filter(Address.id == address_id).values(**address_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(address_object)

    return await get_single_address(session, address_id=address_id, output_schema=AddressBasicOutputSchema)
