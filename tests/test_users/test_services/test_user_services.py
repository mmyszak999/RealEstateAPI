import pytest
from fastapi import BackgroundTasks, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.apps.users.schemas import UserLoginInputSchema, UserOutputSchema
from src.apps.users.services.activation_services import deactivate_single_user
from src.apps.users.services.user_services import (
    authenticate,
    create_single_user,
    create_user_base,
    delete_single_user,
    get_all_users,
    get_single_user,
    update_single_user,
)
from src.core.exceptions import (
    AccountNotActivatedException,
    AlreadyExists,
    AuthenticationException,
    DoesNotExist,
)
from src.core.factory.user_factory import (
    UserRegisterSchemaFactory,
    UserUpdateSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    auth_headers,
    db_staff_user,
    db_superuser,
    db_user,
    staff_auth_headers,
)


@pytest.mark.asyncio
async def test_raise_exception_when_creating_user_with_occupied_email(
    async_session: AsyncSession, db_user: UserOutputSchema
):
    user_schema = UserRegisterSchemaFactory().generate(email=DB_USER_SCHEMA.email)
    with pytest.raises(AlreadyExists):
        await create_user_base(async_session, user_schema)


@pytest.mark.asyncio
async def test_raise_exception_when_providing_wrong_credentials_when_signing_in(
    async_session: AsyncSession, db_user: UserOutputSchema
):
    login_schema = UserLoginInputSchema(email=db_user.email, password="wrongpass")
    with pytest.raises(AuthenticationException):
        await authenticate(login_schema, async_session)


@pytest.mark.asyncio
async def test_raise_exception_when_inactive_user_tries_to_sign_in(
    async_session: AsyncSession,
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
):
    await deactivate_single_user(async_session, db_user.id, db_staff_user.id)
    login_schema = UserLoginInputSchema(email=db_user.email, password="password")
    with pytest.raises(AccountNotActivatedException):
        await authenticate(login_schema, async_session)


@pytest.mark.asyncio
async def test_if_single_user_was_returned(
    async_session: AsyncSession, db_user: UserOutputSchema
):
    user = await get_single_user(async_session, db_user.id)

    assert user.id == db_user.id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_user(
    async_session: AsyncSession, db_user: UserOutputSchema
):
    with pytest.raises(DoesNotExist):
        await get_single_user(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_users_were_returned(
    async_session: AsyncSession,
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
    db_superuser: UserOutputSchema,
):
    users = await get_all_users(async_session, PageParams())
    assert users.total == 3


@pytest.mark.asyncio
async def test_if_inactive_users_will_be_included_in_retrieving_all_users(
    async_session: AsyncSession,
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
    db_superuser: UserOutputSchema,
):
    await deactivate_single_user(async_session, db_user.id, db_staff_user.id)

    active_users = await get_all_users(async_session, PageParams())
    assert active_users.total == 2

    all_users = await get_all_users(async_session, PageParams(), only_active=False)
    assert all_users.total == 3


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_user(
    async_session: AsyncSession, db_user: UserOutputSchema
):
    update_data = UserUpdateSchemaFactory().generate(first_name="test")

    with pytest.raises(DoesNotExist):
        await update_single_user(async_session, update_data, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_deleting_nonexistent_user(
    async_session: AsyncSession,
):
    with pytest.raises(DoesNotExist):
        await delete_single_user(async_session, generate_uuid())
