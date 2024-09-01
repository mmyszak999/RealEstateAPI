from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.companies.schemas import (
    CompanyBasicOutputSchema,
    CompanyInputSchema,
    CompanyOutputSchema,
    CompanyUpdateSchema,
)
from src.apps.companies.services import (
    add_single_user_to_company,
    create_company,
    get_all_companies,
    get_single_company,
    remove_single_user_from_company,
    update_single_company,
)
from src.apps.users.models import User
from src.apps.users.schemas import UserIdSchema
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

company_router = APIRouter(prefix="/companies", tags=["company"])


@company_router.post(
    "/",
    response_model=CompanyBasicOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_company(
    company: CompanyInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CompanyBasicOutputSchema:
    await check_if_staff(request_user)
    return await create_company(session, company)


@company_router.get(
    "/",
    response_model=PagedResponseSchema[CompanyBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_companies(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[CompanyBasicOutputSchema]:
    return await get_all_companies(
        session, page_params, query_params=request.query_params.multi_items()
    )


@company_router.get(
    "/{company_id}",
    response_model=Union[CompanyOutputSchema, CompanyBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_company(
    company_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[CompanyOutputSchema, CompanyBasicOutputSchema]:
    if request_user.is_staff or request_user.company_id == company_id:
        return await get_single_company(session, company_id)
    return await get_single_company(
        session, company_id, output_schema=CompanyBasicOutputSchema
    )


@company_router.patch(
    "/{company_id}",
    response_model=CompanyOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_company(
    company_id: str,
    company_input: CompanyUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CompanyOutputSchema:
    await check_if_staff(request_user)
    return await update_single_company(session, company_input, company_id)


@company_router.patch(
    "/{company_id}/add-user",
    status_code=status.HTTP_200_OK,
)
async def add_user_to_company(
    company_id: str,
    user_company_input: UserIdSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> JSONResponse:
    await check_if_staff(request_user)
    await add_single_user_to_company(session, user_company_input, company_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "The user has been added to the company! "},
    )


@company_router.patch(
    "/{company_id}/remove-user",
    status_code=status.HTTP_200_OK,
)
async def remove_user_from_company(
    company_id: str,
    user_company_input: UserIdSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> JSONResponse:
    await check_if_staff(request_user)
    await remove_single_user_from_company(session, user_company_input, company_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "The user has been removed from the company! "},
    )
