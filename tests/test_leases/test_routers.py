import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.users.schemas import UserOutputSchema, UserIdSchema
from src.apps.leases.schemas import LeaseOutputSchema
from src.core.factory.lease_factory import (
    LeaseInputSchemaFactory,
    LeaseUpdateSchemaFactory,
)
from src.apps.leases.services import get_all_leases
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    auth_headers,
    db_staff_user,
    db_user,
    db_superuser,
    staff_auth_headers,
    superuser_auth_headers
)
from tests.test_leases.conftest import db_leases
from tests.test_addresses.conftest import db_addresses
from tests.test_companies.conftest import db_companies
from tests.test_properties.conftest import db_properties
from src.core.pagination.schemas import PagedResponseSchema
from src.apps.leases.schemas import LeaseOutputSchema
from src.apps.properties.schemas import PropertyOutputSchema


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
            status.HTTP_201_CREATED,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_create_lease(
    async_client: AsyncClient,
    db_superuser: UserOutputSchema,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_properties: PagedResponseSchema[PropertyOutputSchema]
):
    available_property = [
        property for property in db_properties.results if property.owner_id == db_superuser.id
    ][0]
    lease_data = LeaseInputSchemaFactory().generate(
        property_id=available_property.id,
        owner_id=db_superuser.id,
        tenant_id=user.id
    )
    response = await async_client.post(
        "leases/", headers=user_headers, content=lease_data.json()
    )

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
async def test_only_staff_user_can_get_active_leases(
    async_client: AsyncClient,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("leases/", headers=user_headers)

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
async def test_only_staff_user_can_get_all_leases(
    async_client: AsyncClient,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("leases/all", headers=user_headers)

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
async def test_authenticated_user_can_get_their_owner_leases(
    async_client: AsyncClient,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("leases/owner-leases", headers=user_headers)

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
async def test_authenticated_user_can_get_their_tenant_leases(
    async_client: AsyncClient,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("leases/tenant-leases", headers=user_headers)

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
async def test_only_staff_user_can_get_leases_with_renewals_accepted(
    async_client: AsyncClient,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("leases/with-renewals", headers=user_headers)

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
        (
            pytest.lazy_fixture("db_superuser"),
            pytest.lazy_fixture("superuser_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_owner_or_tenant_can_get_their_single_lease(
    async_client: AsyncClient,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        f"leases/{db_leases.results[0].id}", headers=user_headers
    )
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
        (
            pytest.lazy_fixture("db_superuser"),
            pytest.lazy_fixture("superuser_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_or_owner_can_update_single_lease(
    async_client: AsyncClient,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    update_schema = LeaseUpdateSchemaFactory().generate(rent_amount=1234)
    response = await async_client.patch(
        f"leases/{db_leases.results[0].id}",
        headers=user_headers,
        content=update_schema.json(),
    )

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
        (
            pytest.lazy_fixture("db_superuser"),
            pytest.lazy_fixture("superuser_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_or_owner_can_accept_or_discard_lease_renewal(
    async_client: AsyncClient,
    db_leases: PagedResponseSchema[LeaseOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.patch(
        f"leases/{db_leases.results[0].id}/accept-renewal",
        headers=user_headers
    )

    assert response.status_code == status_code
    
    response = await async_client.patch(
        f"leases/{db_leases.results[0].id}/discard-renewal",
        headers=user_headers
    )

    assert response.status_code == status_code
