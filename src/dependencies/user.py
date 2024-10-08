from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.core.exceptions import AccountNotActivatedException, AuthenticationException
from src.dependencies.get_db import get_db
from src.settings.jwt_settings import AuthJWTSettings


async def authenticate_user(
    auth_jwt: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)
) -> User:
    auth_jwt.jwt_required()
    jwt_subject = auth_jwt.get_jwt_subject()
    user = await session.scalar(select(User).filter(User.email == jwt_subject).limit(1))
    if not user:
        raise AuthenticationException("Cannot find user")
    if not user.is_active:
        raise AccountNotActivatedException("email", user.email)

    return user


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()
