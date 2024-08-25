"""import pytest
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
from src.core.exceptions import NoSuchFieldException, UnavailableFilterFieldException
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


def generate_query_string(filter_type, value):
    filter_mapping = {
        "lt": f"wholesale_price__lt={value}",
        "gt": f"wholesale_price__gt={value}",
        "ge": f"name__le={value}",
        "le": f"name__ge={value}",
        "eq": f"weight__eq={value}",
        "ne": f"weight__ne={value}",
    }
    return filter_mapping[filter_type]


@pytest.mark.parametrize(
    "filter_type, attr, result",
    [
        ("lt", "wholesale_price", 0),
        ("gt", "wholesale_price", 1),
        ("ge", "name", 1),
        ("le", "name", 1),
        ("eq", "weight", 1),
        ("ne", "weight", 1),
    ],
)
@pytest.mark.asyncio
async def test_objects_are_filtered_correctly_when_filtering_with_different_configurations(
    async_client: AsyncClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    filter_type: str,
    attr: str,
    result: int,
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
):
    product_data = ProductInputSchemaFactory().generate(
        category_ids=CategoryIdListSchema(id=[db_categories.results[0].id])
    )
    response = await async_client.post(
        "products/", content=product_data.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    value = getattr(db_products.results[0], attr)
    query_string = generate_query_string(filter_type, value)

    response = await async_client.get(
        f"products/?{query_string}", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] >= result


@pytest.mark.asyncio
async def test_if_objects_can_be_filtered_by_multiple_filter_criteria(
    async_client: AsyncClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
):
    product_data = ProductInputSchemaFactory().generate(
        category_ids=CategoryIdListSchema(id=[db_categories.results[0].id]),
    )
    response = await async_client.post(
        "products/", content=product_data.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = await async_client.get(
        f"products/?name__ge={product_data.name}&weight__eq={product_data.weight}",
        headers=staff_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] >= 1


@pytest.mark.asyncio
async def test_if_objects_can_be_filtered_by_multiple_values_in_the_single_criterion(
    async_client: AsyncClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
):
    response = await async_client.get(
        f"products/?name__eq={db_products.results[0].name},{db_products.results[1].name}",
        headers=staff_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2

    
    #filter services tests
    


@pytest.mark.asyncio
async def test_raise_exception_when_using_restricted_field_when_filtering(
    async_client: AsyncClient,
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
):

    with pytest.raises(UnavailableFilterFieldException):
        await get_all_products(
            async_session, PageParams(), query_params=[("id__eq", "some_id")]
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
            query_params=[("no_such_field__eq", "some_value")],
        )
"""