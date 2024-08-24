from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig
from pydantic import BaseSettings, EmailStr
from sqlalchemy import update
from sqlalchemy.orm import Session

from src.apps.emails.schemas import EmailSchema, EmailUpdateSchema
from src.apps.jwt.schemas import ConfirmationTokenSchema
from src.apps.payments.schemas import PaymentAwaitSchema, PaymentConfirmationSchema
from src.apps.user.models import User
from src.core.exceptions import DoesNotExist, IsOccupied, ServiceException
from src.core.utils.utils import (
    check_field_values,
    confirm_token,
    generate_confirm_token,
    if_exists,
    send_email,
)
from src.settings.email_settings import EmailSettings


def email_config(settings: BaseSettings = EmailSettings):
    return ConnectionConfig(**settings().dict())


async def retrieve_email_from_token(session: AsyncSession, token: str) -> str:
    emails = await confirm_token(token)
    current_email = emails[0]
    return current_email


def send_activation_email(
    email: EmailStr, session: Session, background_tasks: BackgroundTasks
) -> None:
    email_schema = EmailSchema(
        email_subject="Activate your account",
        receivers=(email,),
        template_name="account_activation_email.html",
    )
    token = generate_confirm_token([email])
    body_schema = ConfirmationTokenSchema(token=token)
    send_email(email_schema, body_schema, background_tasks, settings=email_config())


def send_awaiting_for_payment_mail(
    email: EmailStr, session: Session,
    background_tasks: BackgroundTasks, order_id: str
) -> None:
    email_schema = EmailSchema(
        email_subject="Awaiting for payment",
        receivers=(email,),
        template_name="awaiting_for_payment.html",
    )
    body_schema = PaymentAwaitSchema(order_id=order_id)
    send_email(email_schema, body_schema, background_tasks, settings=email_config())


def send_payment_confirmaion_mail(
    email: EmailStr, session: Session,
    background_tasks: BackgroundTasks, order_id: str
) -> None:
    email_schema = EmailSchema(
        email_subject="Payment Confirmation",
        receivers=(email,),
        template_name="payment_confirmation.html",
    )
    body_schema = PaymentConfirmationSchema(order_id=order_id)
    send_email(email_schema, body_schema, background_tasks, settings=email_config())