import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.companies.schemas import CompanyOutputSchema
from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.core.factory.company_factory import (
    CompanyInputSchemaFactory,
    CompanyUpdateSchemaFactory,
)
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_companies.conftest import db_companies
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    auth_headers,
    db_staff_user,
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
            status.HTTP_201_CREATED,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_create_company(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    company_data = CompanyInputSchemaFactory().generate()
    response = await async_client.post(
        "companies/", headers=user_headers, content=company_data.json()
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
async def test_staff_and_authenticated_user_can_get_all_companies(
    async_client: AsyncClient,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("companies/", headers=user_headers)

    assert response.status_code == status_code
    assert response.json()["total"] == 3


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
async def test_authenticated_user_can_get_single_company(
    async_client: AsyncClient,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        f"companies/{db_companies.results[0].id}", headers=user_headers
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
async def test_only_staff_user_can_update_single_company(
    async_client: AsyncClient,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    update_schema = CompanyUpdateSchemaFactory().generate(company_name="test_name")
    response = await async_client.patch(
        f"companies/{db_companies.results[0].id}",
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
async def test_only_staff_user_can_add_single_user_to_company(
    async_client: AsyncClient,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_user: UserOutputSchema,
):
    update_schema = UserIdSchema(id=db_user.id)
    response = await async_client.patch(
        f"companies/{db_companies.results[0].id}/add-user",
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
async def test_only_staff_user_can_remove_single_user_from_company(
    async_client: AsyncClient,
    db_companies: PagedResponseSchema[CompanyOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_staff_user: UserOutputSchema,
):
    update_schema = UserIdSchema(id=db_staff_user.id)
    response = await async_client.patch(
        f"companies/{db_companies.results[0].id}/remove-user",
        headers=user_headers,
        content=update_schema.json(),
    )

    assert response.status_code == status_code
