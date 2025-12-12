from typing import Any, Union

from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.emails.services import send_activation_email
from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.users.models import User, Role
from src.apps.users.schemas import (
    UserInfoOutputSchema,
    UserInputSchema,
    UserLoginInputSchema,
    UserOutputSchema,
    UserRegisterSchema,
    UserUpdateSchema,
    RoleInputSchema,
    RoleBaseSchema,
    RoleOutputSchema,
    RoleUpdateSchema
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
from src.settings.general import settings


async def create_user_base(
    session: AsyncSession, user_input: UserRegisterSchema
) -> User:
    user_data = user_input.dict()
    if user_data.pop("password_repeat"):
        user_data["password"] = await hash_user_password(
            password=user_data.pop("password")
        )

    if email_check := await if_exists(User, "email", user_data.get("email"), session):
        raise AlreadyExists(User.__name__, "email", email_check.email)

    if role_check := await if_exists(Role, "name", "user", session):
        user_data["role_id"] = role_check.id
    
    new_user = User(**user_data)
    return new_user


async def create_single_user(
    session: AsyncSession,
    user_input: UserInputSchema,
    background_tasks: BackgroundTasks,
) -> UserInfoOutputSchema:
    new_user = await create_user_base(session, user_input)

    if settings.SEND_EMAILS:
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
        select(User).filter(User.email == login_data["email"]).limit(1)
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
    return AccessTokenOutputSchema(access_token=access_token, user_role=user.role.name)


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
    PagedResponseSchema[UserInfoOutputSchema], PagedResponseSchema[UserOutputSchema]
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

async def set_user_role(
    session: AsyncSession,
    user_id: str,
    role_name: str
) -> UserInfoOutputSchema:
    user = await session.scalar(
        select(User).filter(User.id == user_id).limit(1)
    )
    if not user:
        raise DoesNotExist(User.__name__, "id", user_id)

    role = await session.scalar(
        select(Role).filter(Role.name == role_name).limit(1)
    )
    if not role:
        raise ServiceException(f"Role '{role_name}' does not exist")

    user.role_id = role.id

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return UserInfoOutputSchema.from_orm(user)

async def create_role(
    session: AsyncSession,
    role_input: RoleInputSchema,
) -> RoleOutputSchema:

    role_data = role_input.dict(exclude_none=True)

    # check duplicate
    if found := await if_exists(Role, "name", role_data["name"], session):
        raise AlreadyExists(Role.__name__, "name", found.name)

    new_role = Role(**role_data)

    session.add(new_role)
    await session.commit()
    await session.refresh(new_role)

    return RoleOutputSchema.from_orm(new_role)


async def get_single_role(
    session: AsyncSession,
    role_id: str,
) -> RoleOutputSchema:

    role = await session.scalar(
        select(Role).filter(Role.id == role_id).limit(1)
    )

    if not role:
        raise DoesNotExist(Role.__name__, "id", role_id)

    return RoleOutputSchema.from_orm(role)


async def get_all_roles(
    session: AsyncSession,
    page_params: PageParams,
    query_params: list[tuple] = None,
) -> PagedResponseSchema[RoleOutputSchema]:

    query = select(Role)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Role)

    return await paginate(
        query=query,
        response_schema=RoleOutputSchema,
        table=Role,
        page_params=page_params,
        session=session,
    )


async def update_role(
    session: AsyncSession,
    role_id: str,
    role_input: RoleUpdateSchema,
) -> RoleOutputSchema:

    role = await session.scalar(
        select(Role).filter(Role.id == role_id).limit(1)
    )
    if not role:
        raise DoesNotExist(Role.__name__, "id", role_id)

    update_data = role_input.dict(exclude_unset=True, exclude_none=True)

    if "name" in update_data:
        if found := await if_exists(Role, "name", update_data["name"], session):
            # disallow renaming to existing role
            if found.id != role_id:
                raise AlreadyExists(Role.__name__, "name", update_data["name"])

    if update_data:
        stmt = (
            update(Role)
            .filter(Role.id == role_id)
            .values(**update_data)
        )
        await session.execute(stmt)
        await session.commit()

    return await get_single_role(session, role_id)


"""async def delete_single_user(session: AsyncSession, user_id: str):
    if not (user_object := (await if_exists(User, "id", user_id, session))):
        raise DoesNotExist(User.__name__, "id", user_id)

    statement = delete(User).filter(User.id == user_id)
    result = await session.execute(statement)
    await session.commit()

    return result"""
