from typing import Any, Union

from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.emails.services import send_activation_email
from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.users.models import User
from src.apps.users.schemas import (
    UserInfoOutputSchema,
    UserInputSchema,
    UserLoginInputSchema,
    UserOutputSchema,
    UserUpdateSchema,
    UserRegisterSchema
)
from src.core.exceptions import (
    AccountAlreadyActivatedException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException,
    AlreadyExists,
    AuthenticationException,
    DoesNotExist,
    ServiceException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.crypt import hash_user_password, passwd_context
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists


async def create_user_base(session: AsyncSession, user_input: UserRegisterSchema) -> User:
    user_data = user_input.dict()
    if user_data.pop("password_repeat"):
        user_data["password"] = await hash_user_password(password=user_data.pop("password"))

    if (email_check := await if_exists(User, "email", user_data.get("email"), session)):
        raise AlreadyExists(User.__name__, "email", email_check.email)

    new_user = User(**user_data)
    return new_user


async def create_single_user(
    session: AsyncSession,
    user_input: UserInputSchema,
    background_tasks: BackgroundTasks,
    with_email_activation: bool = False
) -> UserInfoOutputSchema:
    new_user = await create_user_base(session, user_input)
    
    if with_email_activation:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        await send_activation_email(new_user.email, session, background_tasks)
        return UserInfoOutputSchema.from_orm(new_user)

    new_user.is_active = True
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return UserInfoOutputSchema.from_orm(new_user)


async def authenticate(
    user_login_schema: UserLoginInputSchema, session: AsyncSession
) -> User:
    login_data = user_login_schema.dict()
    user = await session.scalar(
        select(User)
        .filter(User.email == login_data["email"])
        .limit(1)
    )
    if not (user and passwd_context.verify(login_data["password"], user.password)):
        raise AuthenticationException("Invalid Credentials")
    if not user.is_active:
        raise AccountNotActivatedException("email", login_data["email"])

    return user


async def get_access_token_schema(
    user_login_schema: UserLoginInputSchema, session: AsyncSession, auth_jwt: AuthJWT
) -> AccessTokenOutputSchema:
    user = await authenticate(user_login_schema, session=session)
    email = user.email
    access_token = auth_jwt.create_access_token(subject=email, algorithm="HS256")
    return AccessTokenOutputSchema(
        access_token=access_token,
        is_staff=user.is_staff
        )


async def get_single_user(
    session: AsyncSession, user_id: str, output_schema: BaseModel = UserOutputSchema
) -> BaseModel:
    if not (user_object := await if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)

    return output_schema.from_orm(user_object)


async def get_all_users(
    session: AsyncSession,
    page_params: PageParams,
    output_schema: BaseModel = UserOutputSchema,
    only_active: bool = True,
    query_params: list[tuple] = None,
) -> Union[
    PagedResponseSchema[UserInfoOutputSchema],
    PagedResponseSchema[UserOutputSchema]
]:
    query = select(User)
    if only_active:
        query = query.filter(User.is_active == True)

    if query_params:
        query = filter_and_sort_instances(query_params, query, User)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=User,
        page_params=page_params,
        session=session,
    )


async def update_single_user(
    session: AsyncSession, user_input: UserUpdateSchema, user_id: str
) -> UserInfoOutputSchema:
    if not (await if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)

    user_data = user_input.dict(exclude_unset=True, exclude_none=True)

    if user_data:
        statement = update(User).filter(User.id == user_id).values(**user_data)

        await session.execute(statement)
        await session.commit()

    return await get_single_user(
        session, user_id=user_id, output_schema=UserInfoOutputSchema
    )


async def delete_single_user(session: AsyncSession, user_id: str):
    if not (user_object := (await if_exists(User, "id", user_id, session))):
        raise DoesNotExist(User.__name__, "id", user_id)

    statement = delete(User).filter(User.id == user_id)
    result = await session.execute(statement)
    await session.commit()

    return result
