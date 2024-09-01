import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.leases.schemas import LeaseOutputSchema
from src.apps.payments.schemas import PaymentOutputSchema
from src.apps.properties.schemas import PropertyOutputSchema
from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_leases.conftest import db_leases
from tests.test_payments.conftest import db_payments
from tests.test_properties.conftest import db_properties
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    auth_headers,
    db_staff_user,
    db_superuser,
    db_user,
    staff_auth_headers,
)


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_403_FORBIDDEN,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_can_get_all_payments(
    async_client: AsyncClient,
    db_payments: PagedResponseSchema[PaymentOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("payments/all", headers=user_headers)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_403_FORBIDDEN,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_can_get_accepted_payments(
    async_client: AsyncClient,
    db_payments: PagedResponseSchema[PaymentOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("payments/accepted", headers=user_headers)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_403_FORBIDDEN,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_can_get_not_accepted_payments(
    async_client: AsyncClient,
    db_payments: PagedResponseSchema[PaymentOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("payments/waiting", headers=user_headers)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_200_OK,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_authenticated_user_can_get_their_payments(
    async_client: AsyncClient,
    db_payments: PagedResponseSchema[PaymentOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("payments/my-payments", headers=user_headers)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_403_FORBIDDEN,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_and_tenant_can_get_the_related_single_payment(
    async_client: AsyncClient,
    db_payments: PagedResponseSchema[PaymentOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        f"payments/{db_payments.results[0].id}", headers=user_headers
    )
    assert response.status_code == status_code
