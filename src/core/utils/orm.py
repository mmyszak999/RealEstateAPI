import uuid
from typing import Any

from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession


async def if_exists(model_class: Table, field: str, value: Any, session: AsyncSession):
    return await session.scalar(
        select(model_class).filter(getattr(model_class, field) == value)
    )


def default_available_slots(context):
    return context.get_current_parameters()["max_stocks"]


def default_available_stock_weight(context):
    return context.get_current_parameters()["max_weight"]


def default_available_sections(context):
    return context.get_current_parameters()["max_sections"]


def default_available_waiting_rooms(context):
    return context.get_current_parameters()["max_waiting_rooms"]


def default_available_section_weight(context):
    return context.get_current_parameters()["max_weight"]


def default_available_section_racks(context):
    return context.get_current_parameters()["max_racks"]


def default_available_rack_weight(context):
    return context.get_current_parameters()["max_weight"]


def default_available_rack_levels(context):
    return context.get_current_parameters()["max_levels"]


def default_available_rack_level_weight(context):
    return context.get_current_parameters()["max_weight"]


def default_available_rack_level_slots(context):
    return context.get_current_parameters()["max_slots"]
