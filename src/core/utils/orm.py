import uuid
from datetime import timedelta
from typing import Any

from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.leases.enums import BillingPeriodEnum


async def if_exists(model_class: Table, field: str, value: Any, session: AsyncSession):
    return await session.scalar(
        select(model_class).filter(getattr(model_class, field) == value)
    )


def default_lease_expiration_date(context):
    return context.get_current_parameters()["end_date"] or None

def default_next_payment_date(context):
    start_date = context.get_current_parameters()["start_date"]
    billing_period = context.get_current_parameters()["billing_period"]
    if billing_period == BillingPeriodEnum.WEEKLY:
        return start_date + timedelta(days=7)
    if billing_period == BillingPeriodEnum.MONTHLY:
        return start_date + timedelta(days=30)
    if billing_period == BillingPeriodEnum.YEARLY:
        return start_date + timedelta(days=365)
