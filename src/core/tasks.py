from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.apps.leases.services import (
    manage_lease_renewals_and_expired_statuses,
    manage_leases_with_incoming_payment_date,
    manage_property_statuses_for_lease_with_the_start_date_being_today,
)
from src.dependencies.get_db import get_db


async def _manage_lease_renewals_and_expired_statuses():
    async for session in get_db():
        await manage_lease_renewals_and_expired_statuses(session)


async def _manage_property_statuses_for_lease_with_the_start_date_being_today():
    async for session in get_db():
        await manage_property_statuses_for_lease_with_the_start_date_being_today(
            session
        )


async def _manage_leases_with_incoming_payment_date():
    async for session in get_db():
        await manage_leases_with_incoming_payment_date(session, BackgroundTasks())


scheduler = AsyncIOScheduler(job_defaults={"max_instances": 2})


"""
in case of testing the features related to the job tasks,
please set jobs intervals on couple seconds for example:

scheduler.add_job(_manage_property_statuses_for_lease_with_the_start_date_being_today, "interval", seconds=15)
"""

scheduler.add_job(
    _manage_lease_renewals_and_expired_statuses, "interval", minutes=60 * 24
)
scheduler.add_job(
    _manage_property_statuses_for_lease_with_the_start_date_being_today,
    "interval",
    minutes=60 * 24,
)
scheduler.add_job(
    _manage_leases_with_incoming_payment_date, "interval", minutes=60 * 12
)
scheduler.start()
