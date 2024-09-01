from sqlalchemy import Table, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.pagination.models import BaseModel, PageParams
from src.core.pagination.schemas import PagedResponseSchema, T


async def paginate(
    query,
    response_schema: BaseModel,
    table: Table,
    page_params: PageParams,
    session: AsyncSession,
) -> PagedResponseSchema[T]:
    total_amount = await session.scalar(
        select(func.count()).select_from(query.subquery())
    )

    instances = await session.execute(
        query.offset((page_params.page - 1) * page_params.size).limit(page_params.size)
    )
    instances = instances.scalars().unique().all()
    total_on_page = len(instances)

    next_page_check = (
        total_amount - ((page_params.page - 1) * page_params.size)
    ) > page_params.size

    return PagedResponseSchema(
        total=total_amount,
        total_on_page=total_on_page,
        page=page_params.page,
        size=page_params.size,
        results=[
            response_schema.from_orm(item) for item in instances[: page_params.size]
        ],
        has_next_page=next_page_check,
    )
