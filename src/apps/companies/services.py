from typing import Union

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.apps.companies.models import Company
from src.apps.companies.schemas import (
    CompanyInputSchema,
    CompanyOutputSchema,
    CompanyUpdateSchema,
    CompanyBasicOutputSchema
)
from src.apps.users.schemas import UserIdSchema
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    UserAlreadyHasCompanyException,
    ServiceException,
    UserHasNoCompanyException
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists
from src.apps.users.models import User


async def create_company(
    session: AsyncSession, company_input: CompanyInputSchema
) -> CompanyBasicOutputSchema:
    company_data = company_input.dict()

    if company_name_check := await if_exists(
        Company, "company_name", company_data.get(company_name), session
    ):
        raise AlreadyExists(Company.__name__, "company_name", company_data.get("company_name"))

    new_company = Company(**company_data)
    session.add(new_company)
    await session.commit()

    return CompanyBasicOutputSchema.from_orm(new_company)


async def get_single_company(
    session: AsyncSession, company_id: str, output_schema: BaseModel = CompanyOutputSchema
) -> Union[
    CompanyOutputSchema,
    CompanyBasicOutputSchema
]:
    if not (company_object := await if_exists(Company, "id", company_id, session)):
        raise DoesNotExist(Company.__name__, "id", company_id)

    return output_schema.from_orm(company_object)


async def get_all_companies(
    session: AsyncSession, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[CompanyBasicOutputSchema]:
    query = select(Company)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Company)

    return await paginate(
        query=query,
        response_schema=CompanyBasicOutputSchema,
        table=Company,
        page_params=page_params,
        session=session,
    )


async def update_single_company(
    session: AsyncSession, company_input: CompanyUpdateSchema, company_id: str
) -> CompanyOutputSchema:
    if not (company_object := await if_exists(Company, "id", company_id, session)):
        raise DoesNotExist(Company.__name__, "id", company_id)

    company_data = company_input.dict(exclude_unset=True)

    if company_data and (company_data.get('company_name') != company_object.company_name):
        company_name_check = await session.scalar(
            select(Company).filter(Company.company_name == company_input.company_name).limit(1)
        )
        if company_name_check:
            raise IsOccupied(Company.__name__, "name", company_input.company_name)

        statement = (
            update(Company).filter(Company.id == company_id).values(**company_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(company_object)

    return await get_single_company(session, company_id=company_id)


async def manage_user_company_status(
    session: AsyncSession, user_company_schema: UserIdSchema, company_id: str, add_user: bool = True
) -> None:
    if not (company_object := await if_exists(Company, "id", company_id, session)):
        raise DoesNotExist(Company.__name__, "id", company_id)
    
    user_id = user_company_schema.id
    if not (user_object := await if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)
    
    if not user_object.is_active:
        raise ServiceException("Inactive user cannot be added or removed from the company! ")
    
    if user_object.company and add_user:
        raise UserAlreadyHasCompanyException
    
    if (not user_object.company and not add_user):
        raise UserHasNoCompanyException
    
    company = company_id if add_user else None
    user_object.company_id = company
    session.add(user_object)
    await session.commit()
    return

async def add_single_user_to_company(
    session: AsyncSession, user_company_schema: UserIdSchema, company_id: str,
) -> None:
    return await manage_user_company_status(
        session, user_company_schema, company_id
    )

async def remove_single_user_from_company(
    session: AsyncSession, user_company_schema: UserIdSchema, company_id: str,
) -> None:
    return await manage_user_company_status(
        session, user_company_schema, company_id, add_user=False
    )
    
        
    
    