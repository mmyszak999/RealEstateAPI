import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.users.schemas import UserOutputSchema, UserIdSchema
from src.apps.addresses.schemas import AddressOutputSchema
from src.core.factory.address_factory import (
    AddressInputSchemaFactory,
    AddressUpdateSchemaFactory,
)
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_addresses.conftest import (
    db_addresses
)
from src.apps.companies.schemas import CompanyOutputSchema
from tests.test_companies.conftest import db_companies
from src.core.pagination.schemas import PagedResponseSchema


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
async def test_only_staff_user_can_create_address(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
):
    address_data = AddressInputSchemaFactory().generate(company_id=db_companies.results[-1].id)
    response = await async_client.post(
        "addresses/", headers=user_headers, content=address_data.json()
    )
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
async def test_staff_and_authenticated_user_can_get_all_addresses(
    async_client: AsyncClient,
    db_addresses: PagedResponseSchema[AddressOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("addresses/", headers=user_headers)

    assert response.status_code == status_code
    assert response.json()["total"] == 5


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
async def test_authenticated_user_can_get_single_address(
    async_client: AsyncClient,
    db_addresses: PagedResponseSchema[AddressOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        f"addresses/{db_addresses.results[0].id}", headers=user_headers
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
        )
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_update_single_address(
    async_client: AsyncClient,
    db_addresses: PagedResponseSchema[AddressOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    update_schema = AddressUpdateSchemaFactory().generate(city="Houston")
    response = await async_client.patch(
        f"addresses/{db_addresses.results[0].id}",
        headers=user_headers,
        content=update_schema.json(),
    )

    assert response.status_code == status_code
