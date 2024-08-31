from typing import Any

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.emails.services import retrieve_email_from_token
from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.users.models import User
from src.apps.users.schemas import (
    UserInfoOutputSchema,
    UserInputSchema,
    UserLoginInputSchema,
    UserOutputSchema,
    UserPasswordSchema,
    UserUpdateSchema,
)
from src.core.exceptions import (
    AccountAlreadyActivatedException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException,
    AuthenticationException,
    DoesNotExist,
    ServiceException,
    UserCantActivateTheirAccountException,
    UserCantDeactivateTheirAccountException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.crypt import hash_user_password, passwd_context
from src.core.utils.email import confirm_token
from src.core.utils.orm import if_exists


async def manage_activation_status(
    session: AsyncSession,
    field: str,
    value: Any,
    activate: bool = True,
) -> None:
    if not (user_object := (await if_exists(User, field, value, session))):
        raise DoesNotExist(User.__name__, field, value)

    if activate and user_object.is_active:
        raise AccountAlreadyActivatedException("email", user_object.email)

    if (not activate) and (not user_object.is_active):
        raise AccountAlreadyDeactivatedException("email", user_object.email)

    user_object.is_active = activate
    session.add(user_object)

    await session.commit()


async def activate_single_user(
    session: AsyncSession, user_id: str, request_user_id: str
) -> None:
    if user_id == request_user_id:
        raise UserCantActivateTheirAccountException

    await manage_activation_status(session, "id", user_id)


async def activate_single_user_by_link(
    session: AsyncSession, field: str, value: Any
) -> None:
    await manage_activation_status(session, field, value)


async def deactivate_single_user(
    session: AsyncSession, user_id: str, request_user_id: str
) -> None:
    if user_id == request_user_id:
        raise UserCantDeactivateTheirAccountException

    await manage_activation_status(session, "id", user_id, activate=False)


async def activate_account_service(
    session: AsyncSession, token: str
) -> None:
    user_email = await retrieve_email_from_token(session, token)
    await activate_single_user_by_link(session, "email", user_email)
