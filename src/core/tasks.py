from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.leases.services import (
    manage_lease_renewals_and_expired_statuses,
    manage_property_statuses_for_lease_with_the_start_date_being_today,
    manage_leases_with_incoming_payment_date
)

from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user
from src.settings.db_settings import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def _manage_lease_renewals_and_expired_statuses():
    async for session in get_db():
        await manage_lease_renewals_and_expired_statuses(session)


async def _manage_property_statuses_for_lease_with_the_start_date_being_today():
    async for session in get_db():
        await manage_property_statuses_for_lease_with_the_start_date_being_today(session)


async def _manage_leases_with_incoming_payment_date():
    async for session in get_db():
        await manage_leases_with_incoming_payment_date(session, BackgroundTasks())


scheduler = AsyncIOScheduler()
    
scheduler.add_job(_manage_lease_renewals_and_expired_statuses, "interval", minutes=60*24)
scheduler.add_job(_manage_property_statuses_for_lease_with_the_start_date_being_today, "interval", minutes=60*24)
scheduler.add_job(_manage_leases_with_incoming_payment_date, "interval", seconds=60)
scheduler.start()

