from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.leases.schemas import (
    LeaseBasicOutputSchema,
    LeaseInputSchema,
    LeaseOutputSchema,
    LeaseUpdateSchema,
)
from src.apps.leases.services import (
    accept_single_lease_renewal,
    create_lease,
    discard_single_lease_renewal,
    get_all_leases,
    get_single_lease,
    update_single_lease,
)
from src.apps.properties.services import get_single_property
from src.apps.users.models import User
from src.core.exceptions import AuthorizationException
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

lease_router = APIRouter(prefix="/leases", tags=["lease"])


@lease_router.post(
    "/",
    response_model=LeaseBasicOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_lease(
    lease: LeaseInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> LeaseBasicOutputSchema:
    property = await get_single_property(session, lease.property_id)
    await check_if_staff_or_owner(request_user, "id", property.owner_id)
    return await create_lease(session, lease)


@lease_router.get(
    "/all",
    response_model=PagedResponseSchema[LeaseBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_every_lease(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[LeaseBasicOutputSchema]:
    await check_if_staff(request_user)
    return await get_all_leases(
        session,
        page_params,
        query_params=request.query_params.multi_items(),
    )


@lease_router.get(
    "/",
    response_model=PagedResponseSchema[LeaseBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_active_leases(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[LeaseBasicOutputSchema]:
    await check_if_staff(request_user)
    return await get_all_leases(
        session,
        page_params,
        get_active=True,
        query_params=request.query_params.multi_items(),
    )


@lease_router.get(
    "/owner-leases",
    response_model=PagedResponseSchema[LeaseBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_user_owner_leases(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[LeaseBasicOutputSchema]:
    return await get_all_leases(
        session,
        page_params,
        user_id_owner_leases=request_user.id,
        query_params=request.query_params.multi_items(),
    )


@lease_router.get(
    "/tenant-leases",
    response_model=PagedResponseSchema[LeaseBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_user_tenant_leases(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[LeaseBasicOutputSchema]:
    return await get_all_leases(
        session,
        page_params,
        user_id_tenant_leases=request_user.id,
        query_params=request.query_params.multi_items(),
    )


@lease_router.get(
    "/with-renewals",
    response_model=PagedResponseSchema[LeaseBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_leases_with_renewal_accepted(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[LeaseBasicOutputSchema]:
    await check_if_staff(request_user)
    return await get_all_leases(
        session,
        page_params,
        get_with_renewal_accepted=True,
        query_params=request.query_params.multi_items(),
    )


@lease_router.get(
    "/{lease_id}",
    response_model=Union[LeaseOutputSchema, LeaseBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_lease(
    lease_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[LeaseOutputSchema, LeaseBasicOutputSchema]:
    lease = await get_single_lease(session, lease_id)
    if (
        request_user.is_staff
        or getattr(request_user, "id") == lease.owner_id
        or getattr(request_user, "id") == lease.tenant_id
    ):
        return lease
    raise AuthorizationException("You don't have permissions to perform this action! ")


@lease_router.patch(
    "/{lease_id}",
    response_model=LeaseBasicOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_lease(
    lease_id: str,
    lease_input: LeaseUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> LeaseOutputSchema:
    lease = await get_single_lease(session, lease_id)
    await check_if_staff_or_owner(request_user, "id", lease.owner_id)
    return await update_single_lease(session, lease_input, lease_id)


@lease_router.patch(
    "/{lease_id}/accept-renewal",
    status_code=status.HTTP_200_OK,
)
async def accept_lease_renewal(
    lease_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> JSONResponse:
    lease = await get_single_lease(session, lease_id)
    if (
        request_user.is_staff
        or getattr(request_user, "id") == lease.owner_id
        or getattr(request_user, "id") == lease.tenant_id
    ):
        await accept_single_lease_renewal(session, lease_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "The lease renewal has been accepted! "},
        )
    raise AuthorizationException("You don't have permissions to perform this action!")


@lease_router.patch(
    "/{lease_id}/discard-renewal",
    status_code=status.HTTP_200_OK,
)
async def discard_lease_renewal(
    lease_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> JSONResponse:
    lease = await get_single_lease(session, lease_id)
    if (
        request_user.is_staff
        or getattr(request_user, "id") == lease.owner_id
        or getattr(request_user, "id") == lease.tenant_id
    ):
        await discard_single_lease_renewal(session, lease_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "The lease renewal has been discarded! "},
        )
    raise AuthorizationException("You don't have permissions to perform this action!")
