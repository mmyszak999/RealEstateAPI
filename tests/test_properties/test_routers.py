import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.users.schemas import UserOutputSchema, UserIdSchema
from src.apps.properties.schemas import PropertyOutputSchema
from src.core.factory.property_factory import (
    PropertyInputSchemaFactory,
    PropertyUpdateSchemaFactory,
)
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_properties.conftest import (
    db_properties
)
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
async def test_only_staff_user_can_create_property(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    property_data = PropertyInputSchemaFactory().generate()
    response = await async_client.post(
        "properties/", headers=user_headers, content=property_data.json()
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
async def test_authenticated_user_can_get_available_properties(
    async_client: AsyncClient,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("properties/", headers=user_headers)

    assert response.status_code == status_code
    assert response.json()["total"] == 3


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
async def test_only_staff_user_can_get_all_properties(
    async_client: AsyncClient,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("properties/all", headers=user_headers)

    assert response.status_code == status_code
    
    if status == status.HTTP_200_OK:
        assert response.json()["total"] == 4


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
async def test_authenticated_user_can_get_single_property(
    async_client: AsyncClient,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        f"properties/{db_properties.results[0].id}", headers=user_headers
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
async def test_only_staff_user_can_update_single_property(
    async_client: AsyncClient,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    update_schema = PropertyUpdateSchemaFactory().generate(description="description")
    response = await async_client.patch(
        f"properties/{db_properties.results[0].id}",
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
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_change_property_owner(
    async_client: AsyncClient,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_user: UserOutputSchema
):
    update_schema = UserIdSchema(id=db_user.id)
    response = await async_client.patch(
        f"properties/{db_properties.results[0].id}/change-owner", headers=user_headers,
        content=update_schema.json()
    )

    assert response.status_code == status_code