from typing import Union

import stripe
from fastapi import BackgroundTasks, Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.payments.schemas import (
    PaymentOutputSchema,
    StripePublishableKeySchema,
    StripeSessionSchema,
    PaymentBaseOutputSchema
)
from src.apps.payments.services import (
    get_all_payments,
    get_publishable_key,
    get_single_payment,
    handle_stripe_webhook_event,
)
from src.apps.users.models import User
from src.core.exceptions import AuthorizationException
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user
from src.settings.stripe import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_router = APIRouter(prefix="/stripe", tags=["stripe"])
payment_router = APIRouter(prefix="/payments", tags=["payment"])


@stripe_router.post(
    "/webhook/",
    status_code=status.HTTP_200_OK,
)
async def handle_webhook_event(
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
) -> None:
    return await handle_stripe_webhook_event(session, request, background_tasks)


@payment_router.get(
    "/all",
    response_model=Union[
        PagedResponseSchema[PaymentBaseOutputSchema],
        PagedResponseSchema[PaymentOutputSchema]
],
    status_code=status.HTTP_200_OK,
)
async def get_payments(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
        PagedResponseSchema[PaymentBaseOutputSchema],
        PagedResponseSchema[PaymentOutputSchema]
]:
    await check_if_staff(request_user)
    return await get_all_payments(session, page_params, request.query_params.multi_items())


@payment_router.get(
    "/accepted",
    response_model=Union[
        PagedResponseSchema[PaymentBaseOutputSchema],
        PagedResponseSchema[PaymentOutputSchema]
],
    status_code=status.HTTP_200_OK,
)
async def get_accepted_payments(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
        PagedResponseSchema[PaymentBaseOutputSchema],
        PagedResponseSchema[PaymentOutputSchema]
]:
    await check_if_staff(request_user)
    return await get_all_payments(session, page_params, request.query_params.multi_items(), get_accepted=True)


@payment_router.get(
    "/waiting",
    response_model=Union[
        PagedResponseSchema[PaymentBaseOutputSchema],
        PagedResponseSchema[PaymentOutputSchema]
],
    status_code=status.HTTP_200_OK,
)
async def get_waiting_payments(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
        PagedResponseSchema[PaymentBaseOutputSchema],
        PagedResponseSchema[PaymentOutputSchema]
]:
    await check_if_staff(request_user)
    return await get_all_payments(session, page_params, request.query_params.multi_items(), get_waiting=True)


@payment_router.get(
    "/my-payments",
    response_model=Union[
        PagedResponseSchema[PaymentBaseOutputSchema],
        PagedResponseSchema[PaymentOutputSchema]
],
    status_code=status.HTTP_200_OK,
)
async def get_user_payments(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
        PagedResponseSchema[PaymentBaseOutputSchema],
        PagedResponseSchema[PaymentOutputSchema]
]:
    return await get_all_payments(
        session, page_params, request.query_params.multi_items(), tenant_id=request_user.id
    )


@payment_router.get(
    "/{payment_id}",
    response_model=Union[PaymentOutputSchema, PaymentBaseOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_payment(
    payment_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[PaymentOutputSchema, PaymentBaseOutputSchema]:
    payment = await get_single_payment(session, payment_id)
    if await check_if_staff_or_owner(request_user, "id", payment.tenant.id):
        return payment
    return AuthorizationException("You have no permissions to perform this action! ")
