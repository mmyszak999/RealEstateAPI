from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.properties.schemas import (
    PropertyInputSchema,
    PropertyOutputSchema,
    PropertyUpdateSchema,
    PropertyBasicOutputSchema
)
from src.apps.properties.services import (
    create_property,
    get_all_properties,
    get_single_property,
    update_single_property,
    delete_single_property
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

property_router = APIRouter(prefix="/properties", tags=["property"])


@property_router.post(
    "/",
    response_model=PropertyOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_property(
    property: PropertyInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> PropertyOutputSchema:
    await check_if_staff(request_user)
    return await create_property(session, property)


@property_router.get(
    "/all",
    response_model=PagedResponseSchema[PropertyOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_every_property(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[PropertyOutputSchema]:
    return await get_all_properties(
        session, page_params, query_params=request.query_params.multi_items(),
    )

@property_router.get(
    "/",
    response_model=PagedResponseSchema[PropertyBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_available_properties(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[PropertyBasicOutputSchema]:
    return await get_all_properties(
        session, page_params, get_available=True,
        query_params=request.query_params.multi_items(),
    )

@property_router.get(
    "/rented",
    response_model=PagedResponseSchema[PropertyBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_rented_properties(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[PropertyBasicOutputSchema]:
    return await get_all_properties(
        session, page_params, get_rented=True,
        query_params=request.query_params.multi_items(),
    )


@property_router.get(
    "/{property_id}",
    response_model=PropertyOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_property(
    property_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> PropertyOutputSchema:
    await check_if_staff(request_user)
    return await get_single_property(session, property_id)


@property_router.patch(
    "/{property_id}",
    response_model=PropertyBasicOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_property(
    property_id: str,
    property_input: PropertyUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> PropertyOutputSchema:
    property = await get_single_property(session, property_id)
    await check_if_staff_or_owner(request_user, "id", property.owner_id)
    return await update_single_property(session, property_input, property_id)

@property_router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_property(
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    await check_if_staff(request_user)
    await delete_single_property(session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
