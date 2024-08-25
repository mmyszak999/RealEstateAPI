"""from decimal import Decimal

import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.category_schemas import (
    CategoryIdListSchema,
    CategoryOutputSchema,
)
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.products.services.product_services import get_all_products
from src.apps.users.schemas import UserOutputSchema
from src.core.exceptions import NoSuchFieldException, UnavailableSortFieldException
from src.core.factory.product_factory import ProductInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_products.conftest import db_categories, db_products
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)

@pytest.mark.parametrize(
    "query_string, weight, name",
    [
        ("weight__desc", 15, "aaaaaa"),
        ("name__asc", 15, "aaaaaa"),
    ],
)
@pytest.mark.asyncio
async def test_objects_are_sorted_correctly_when_sorting_with_different_configurations(
    async_client: AsyncClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    query_string: str,
    weight: Decimal,
    name: str,
    db_categories: PagedResponseSchema[CategoryOutputSchema],
):
    product_data_1 = ProductInputSchemaFactory().generate(
        category_ids=CategoryIdListSchema(id=[db_categories.results[0].id]),
        weight=weight,
        name=name,
    )
    response_1 = await async_client.post(
        "products/", content=product_data_1.json(), headers=staff_auth_headers
    )
    assert response_1.status_code == status.HTTP_201_CREATED

    product_data_2 = ProductInputSchemaFactory().generate(
        category_ids=CategoryIdListSchema(id=[db_categories.results[0].id]),
    )
    response_2 = await async_client.post(
        "products/", content=product_data_2.json(), headers=staff_auth_headers
    )
    assert response_2.status_code == status.HTTP_201_CREATED

    response_3 = await async_client.get(
        f"products/?sort={query_string}", headers=staff_auth_headers
    )
    assert response_3.status_code == status.HTTP_200_OK
    assert response_3.json()["results"][0]["id"] == response_1.json()["id"]


@pytest.mark.asyncio
async def test_if_objects_can_be_sorted_by_multiple_sort_criteria(
    async_client: AsyncClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_categories: PagedResponseSchema[CategoryOutputSchema],
):
    product_data_1 = ProductInputSchemaFactory().generate(
        category_ids=CategoryIdListSchema(id=[db_categories.results[0].id]),
        weight=1.1,
        name="cccc",
    )
    response_1 = await async_client.post(
        "products/", content=product_data_1.json(), headers=staff_auth_headers
    )
    assert response_1.status_code == status.HTTP_201_CREATED

    product_data_2 = ProductInputSchemaFactory().generate(
        category_ids=CategoryIdListSchema(id=[db_categories.results[0].id]),
        weight=1.1,
        name="dddd",
    )
    response_2 = await async_client.post(
        "products/", content=product_data_2.json(), headers=staff_auth_headers
    )
    assert response_2.status_code == status.HTTP_201_CREATED

    response_3 = await async_client.get(
        f"products/?sort=weight__asc,name__desc", headers=staff_auth_headers
    )
    assert response_3.status_code == status.HTTP_200_OK
    assert response_3.json()["total"] == 2
    assert response_3.json()["results"][0]["id"] == response_2.json()["id"]
    assert response_3.json()["results"][1]["id"] == response_1.json()["id"]

    
    #sort services tests
    


@pytest.mark.asyncio
async def test_raise_exception_when_using_restricted_field_when_sorting(
    async_client: AsyncClient,
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
):

    with pytest.raises(UnavailableSortFieldException):
        await get_all_products(
            async_session, PageParams(), query_params=[("sort", "id__desc=some id")]
        )


@pytest.mark.asyncio
async def test_raise_exception_when_model_does_not_contain_requested_filter_field(
    async_client: AsyncClient,
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
):

    with pytest.raises(NoSuchFieldException):
        await get_all_products(
            async_session,
            PageParams(),
            query_params=[("sort", "no_such_field__desc=what")],
        )
"""