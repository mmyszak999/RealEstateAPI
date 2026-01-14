from typing import Union

from fastapi import Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.properties.schemas import (
    PropertyBasicOutputSchema,
    PropertyInputSchema,
    PropertyOutputSchema,
    PropertyOwnerIdSchema,
    PropertyUpdateSchema,
)
from src.apps.properties.services import (
    change_property_owner,
    create_property,
    get_all_properties,
    get_single_property,
    update_single_property,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user
from src.core.permissions import role_required  # <-- kluczowe

property_router = APIRouter(prefix="/properties", tags=["property"])


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------
@property_router.post(
    "/",
    response_model=PropertyBasicOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
@role_required("admin", "staff")
async def post_property(
    property: PropertyInputSchema,
    session: AsyncSession = Depends(get_db),
) -> PropertyBasicOutputSchema:
    return await create_property(session, property)


# ---------------------------------------------------------
# GET ALL (STAFF ONLY)
# ---------------------------------------------------------
@property_router.get(
    "/all",
    response_model=PagedResponseSchema[PropertyBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
@role_required("admin", "staff")
async def get_every_property(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[PropertyBasicOutputSchema]:
    return await get_all_properties(
        session,
        page_params,
        query_params=request.query_params.multi_items(),
    )


# ---------------------------------------------------------
# GET AVAILABLE (PUBLIC)
# ---------------------------------------------------------
@property_router.get(
    "/",
    response_model=PagedResponseSchema[PropertyBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_available_properties(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[PropertyBasicOutputSchema]:
    return await get_all_properties(
        session,
        page_params,
        get_available=True,
        query_params=request.query_params.multi_items(),
    )


# ---------------------------------------------------------
# GET RENTED (STAFF ONLY)
# ---------------------------------------------------------
@property_router.get(
    "/rented",
    response_model=PagedResponseSchema[PropertyBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
@role_required("admin", "staff")
async def get_rented_properties(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[PropertyBasicOutputSchema]:
    return await get_all_properties(
        session,
        page_params,
        get_rented=True,
        query_params=request.query_params.multi_items(),
    )


# ---------------------------------------------------------
# MY PROPERTIES (OWNER ONLY)
# ---------------------------------------------------------
@property_router.get(
    "/my-properties",
    response_model=PagedResponseSchema[PropertyBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
@role_required("admin", "staff", "user")  # dowolny zalogowany
async def get_user_owner_leases(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    user: User = Depends(authenticate_user),
) -> PagedResponseSchema[PropertyBasicOutputSchema]:
    return await get_all_properties(
        session,
        page_params,
        owner_id=user.id,
        query_params=request.query_params.multi_items(),
    )


# ---------------------------------------------------------
# GET SINGLE PROPERTY (ROLE OR OWNER)
# ---------------------------------------------------------
@property_router.get(
    "/{property_id}",
    response_model=Union[PropertyOutputSchema, PropertyBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
@role_required("admin", "staff", allow_owner=True, owner_field="property_id")
async def get_property(
    property_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(authenticate_user),
) -> Union[PropertyOutputSchema, PropertyBasicOutputSchema]:

    property = await get_single_property(session, property_id)

    # Jeśli admin/staff albo owner — pełne dane
    if request_user.role.name in {"admin", "staff"} or request_user.id == property.owner_id:
        return property

    # W przeciwnym razie dane podstawowe
    return await get_single_property(
        session, property_id, output_schema=PropertyBasicOutputSchema
    )


# ---------------------------------------------------------
# UPDATE PROPERTY (ROLE OR OWNER)
# ---------------------------------------------------------
@property_router.patch(
    "/{property_id}",
    response_model=PropertyBasicOutputSchema,
    status_code=status.HTTP_200_OK,
)
@role_required("admin", "staff", allow_owner=True, owner_field="property_id")
async def update_property(
    property_id: str,
    property_input: PropertyUpdateSchema,
    session: AsyncSession = Depends(get_db),
) -> PropertyOutputSchema:
    return await update_single_property(session, property_input, property_id)


# ---------------------------------------------------------
# CHANGE OWNER (STAFF ONLY)
# ---------------------------------------------------------
@property_router.patch(
    "/{property_id}/change-owner",
    status_code=status.HTTP_200_OK,
)
@role_required("admin", "staff")
async def change_single_property_owner(
    property_id: str,
    property_schema: PropertyOwnerIdSchema,
    session: AsyncSession = Depends(get_db),
) -> PropertyOutputSchema:
    await change_property_owner(session, property_schema, property_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "The property ownership has been changed!"},
    )
