from typing import Any

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
from itsdangerous import URLSafeTimedSerializer
from pydantic import BaseModel, BaseSettings

from src.settings.general import settings


async def generate_confirm_token(objects: list[str]) -> str:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(objects, salt=settings.SECURITY_PASSWORD_SALT)


async def confirm_token(token: str, expiration=3600) -> list[str]:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        objects = serializer.loads(
            token, salt=settings.SECURITY_PASSWORD_SALT, max_age=expiration
        )
        return objects

    except Exception:
        return False


async def send_email(
    schema: BaseModel,
    body_schema: BaseModel,
    background_tasks: BackgroundTasks,
    settings: BaseSettings,
):
    email_message = MessageSchema(
        subject=schema.email_subject,
        recipients=schema.receivers,
        template_body=body_schema.dict(),
        subtype="html",
    )
    print(email_message.body, email_message.recipients, email_message.subject, email_message.template_body, email_message.reply_to, "xd")
    fast_mail = FastMail(settings)
    background_tasks.add_task(
        fast_mail.send_message, email_message, template_name=schema.template_name
    )
    await background_tasks()
