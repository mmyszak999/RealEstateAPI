import datetime
from typing import Any, Union

import stripe
from fastapi import BackgroundTasks, Request
from pydantic import BaseSettings, BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.payments.models import Payment
from src.apps.payments.schemas import (
    PaymentOutputSchema,
    StripePublishableKeySchema,
    StripeSessionSchema,
    PaymentBaseOutputSchema,
    PaymentAwaitSchema,
    PaymentConfirmationSchema
)
from src.apps.emails.services import (
    send_awaiting_for_payment_mail,
    send_payment_confirmation_mail,
    send_activation_email
)
from src.apps.users.models import User
from src.apps.leases.models import Lease
from src.core.exceptions import (
    DoesNotExist,
    PaymentAlreadyAccepted,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists, get_billing_period_time_span_between_payments
from src.settings.stripe import settings as stripe_settings


async def create_payment(
    session: AsyncSession, lease: Lease, background_tasks: BackgroundTasks
) -> PaymentOutputSchema:
    new_payment = Payment(
        created_at=lease.next_payment_date,
        lease_id=lease.id,
        tenant_id=lease.tenant_id,
    )
    session.add(new_payment)
    await session.flush()
    
    stripe_session = await get_stripe_session_data(
        session, new_payment.id
    )
    new_payment.payment_checkout_url = stripe_session.url
    session.add(new_payment)
    
    next_payment_date = get_billing_period_time_span_between_payments(
        lease.next_payment_date, lease.billing_period
    )
    next_payment_date = min(next_payment_date, lease.lease_expiration_date)
    lease.next_payment_date = next_payment_date
    session.add(lease)
    
    await session.commit()
    body_schema = PaymentAwaitSchema(
        lease_id=lease.id,
        payment_id=new_payment.id,
        tenant_id=lease.tenant_id,
        rent_amount=lease.rent_amount,
        created_at=new_payment.created_at,
        payment_checkout_url=new_payment.payment_checkout_url
    )
    
    await send_awaiting_for_payment_mail(lease.tenant.email, session, background_tasks, body_schema)

    
async def get_single_payment(
    session: AsyncSession, payment_id: str, as_staff: bool = False, output_schema: BaseModel=PaymentOutputSchema
) -> Union[
        PaymentOutputSchema,
        PaymentBaseOutputSchema
        ]:
    if not (payment_object := await if_exists(Payment, "id", payment_id, session)):
        raise DoesNotExist(Payment.__name__, "id", payment_id)

    return output_schema.from_orm(payment_object)


async def get_all_payments(
    session: AsyncSession,
    page_params: PageParams,
    query_params: list[tuple] = None,
    output_schema=PaymentBaseOutputSchema,
    get_accepted: bool = False,
    get_waiting: bool = False,
    tenant_id: str = None
) -> Union[
        PagedResponseSchema[PaymentBaseOutputSchema],
        PagedResponseSchema[PaymentOutputSchema]
]:
    query = select(Payment)
    
    if get_accepted:
        query = query.filter(Payment.payment_accepted == True)
        
    if get_waiting:
        query = query.filter(Payment.waiting_for_payment == True)

    if tenant_id:
        query = query.filter(Payment.tenant_id == tenant_id)
    
    if query_params:
        query = filter_and_sort_instances(query_params, query, Payment)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=Payment,
        page_params=page_params,
        session=session,
    )




"""
    stripe-related services
"""

async def get_publishable_key() -> StripePublishableKeySchema:
    return StripePublishableKeySchema(publishable_key=str(
        stripe_settings.STRIPE_PUBLISHABLE_KEY)
    )



async def create_checkout_session(
    payment_data: dict[str, Any], payment: Payment,
    settings: BaseSettings=stripe_settings
):
    checkout_session = stripe.checkout.Session.create(
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
            payment_method_types=["card"],
            mode="payment",
            line_items=[payment_data],
            metadata={
                "tenant_id": payment.tenant_id, "lease_id": payment.lease_id, "payment_id": payment.id
            }
        )
    return checkout_session
    

async def get_stripe_session_data(session: AsyncSession, payment_id: str) -> StripeSessionSchema:
    if not (payment_object := await if_exists(Payment, "id", payment_id, session)):
        raise DoesNotExist(Payment.__name__, "id", payment_id)
    
    if payment_object.payment_accepted or (not payment_object.waiting_for_payment):
        raise PaymentAlreadyAccepted

    price_data = {
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"Lease payment #{payment_object.id}",
                },
                "unit_amount": int(payment_object.lease.rent_amount * 100),
            },
            "quantity": 1,
        }

    stripe_checkout_session = await create_checkout_session(
        price_data, payment_object
    )
    
    return StripeSessionSchema(
        session_id=stripe_checkout_session["id"],
        url=stripe_checkout_session["url"]
    )

async def handle_stripe_webhook_event(
    session: AsyncSession,
    request: Request,
    background_tasks: BackgroundTasks,
    settings: BaseSettings=stripe_settings
):
    endpoint_secret = settings.WEBHOOK_SECRET
    payload = await request.body()
    sig_header = request.headers["stripe-signature"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as err:
        raise Exception
    except stripe.error.SignatureVerificationError as err:
        raise Exception

    if event["type"] == "checkout.session.completed":
        stripe_session = event["data"]["object"]
        payment_intent = stripe.PaymentIntent.retrieve(id=stripe_session["payment_intent"])
        await fulfill_payment(session, stripe_session, payment_intent, background_tasks)
    return

async def fulfill_payment(
    session: AsyncSession, stripe_session, payment_intent, background_tasks: BackgroundTasks
) -> None:
    print(stripe_session, "gang", payment_intent)
    payment_id = stripe_session["metadata"]["payment_id"]
    amount = payment_intent["amount"] / 100
    stripe_charge_id = payment_intent["latest_charge"]
    
    if not (payment_object := await if_exists(Payment, "id", payment_id, session)):
        raise DoesNotExist(Payment.__name__, "id", payment_id)
    
    if payment_object.payment_accepted or (not payment_object.waiting_for_payment):
        raise PaymentAlreadyAccepted
    
    payment_object.stripe_charge_id = stripe_charge_id
    payment_object.amount = amount
    payment_object.waiting_for_payment = False
    payment_object.payment_accepted = True
    payment_object.payment_date = datetime.date.today()
    session.add(payment_object)
    await session.commit()
    
    body_schema = PaymentConfirmationSchema(
        lease_id=payment_object.lease_id,
        payment_id=payment_object.id,
        tenant_id=payment_object.tenant_id,
        rent_amount=payment_object.lease.rent_amount,
        created_at=payment_object.created_at,
        payment_checkout_url=payment_object.payment_checkout_url
    )
    print("gg", body_schema)
    await send_payment_confirmation_mail(
        payment_object.tenant.email, session, background_tasks, body_schema
    )
    
    
    
    