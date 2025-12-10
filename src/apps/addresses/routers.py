from typing import Union

from fastapi import Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.addresses.schemas import (
    AddressBasicOutputSchema,
    AddressInputSchema,
    AddressOutputSchema,
    AddressUpdateSchema,
)
from src.apps.addresses.services import (
    create_address,
    get_all_addresses,
    get_single_address,
    update_single_address,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import role_required
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user


address_router = APIRouter(prefix="/addresses", tags=["address"])


# ------------------------------------------------
# Create address (admin/staff only)
# ------------------------------------------------
@address_router.post(
    "/",
    response_model=AddressBasicOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
@role_required("admin", "staff")
async def post_address(
    address: AddressInputSchema,
    session: AsyncSession = Depends(get_db),
) -> AddressBasicOutputSchema:
    return await create_address(session, address)


# ------------------------------------------------
# List all addresses (any authenticated user)
# ------------------------------------------------
@address_router.get(
    "/",
    response_model=PagedResponseSchema[AddressBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
@role_required("admin", "staff", "user")
async def get_addresses(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[AddressBasicOutputSchema]:
    return await get_all_addresses(
        session,
        page_params,
        query_params=request.query_params.multi_items(),
    )


# ------------------------------------------------
# Get single address
#   admin/staff → full schema
#   user → basic schema
# ------------------------------------------------
@address_router.get(
    "/{address_id}",
    response_model=Union[AddressOutputSchema, AddressBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
@role_required("admin", "staff", "user")
async def get_address(
    address_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[AddressOutputSchema, AddressBasicOutputSchema]:

    # Admin/staff → full schema
    if request_user.role and request_user.role.name in ("admin", "staff"):
        return await get_single_address(session, address_id)

    # Regular user → restricted schema
    return await get_single_address(
        session,
        address_id,
        output_schema=AddressBasicOutputSchema,
    )


# ------------------------------------------------
# Update address (admin/staff only)
# ------------------------------------------------
@address_router.patch(
    "/{address_id}",
    response_model=AddressBasicOutputSchema,
    status_code=status.HTTP_200_OK,
)
@role_required("admin", "staff")
async def update_address(
    address_id: str,
    address_input: AddressUpdateSchema,
    session: AsyncSession = Depends(get_db),
) -> AddressBasicOutputSchema:
    return await update_single_address(session, address_input, address_id)
