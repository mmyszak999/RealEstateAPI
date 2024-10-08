from datetime import date, timedelta
from typing import Any

from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.leases.enums import BillingPeriodEnum


async def if_exists(
    model_class: Table, field: str, value: Any, session: AsyncSession
) -> Table:
    return await session.scalar(
        select(model_class).filter(getattr(model_class, field) == value)
    )


def default_lease_expiration_date(context):
    return context.get_current_parameters()["end_date"] or None


def default_next_payment_date(context):
    start_date = context.get_current_parameters()["start_date"]
    billing_period = context.get_current_parameters()["billing_period"]
    end_date = context.get_current_parameters().get("end_date", None)

    next_payment, _ = get_billing_period_time_span_between_payments(
        start_date, billing_period
    )

    if end_date:
        return min(next_payment, end_date)
    return next_payment


def get_billing_period_time_span_between_payments(
    start_date: date, billing_period: BillingPeriodEnum
) -> date:
    time_span_in_days = None
    if billing_period == BillingPeriodEnum.WEEKLY:
        next_payment = start_date + timedelta(days=7)
        time_span_in_days = 7
    if billing_period == BillingPeriodEnum.MONTHLY:
        next_payment = start_date + timedelta(days=30)
        time_span_in_days = 30
    if billing_period == BillingPeriodEnum.YEARLY:
        next_payment = start_date + timedelta(days=365)
        time_span_in_days = 365

    return next_payment, time_span_in_days
