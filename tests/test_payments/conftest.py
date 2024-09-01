from typing import Any

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from src.apps.payments.models import Payment
from src.apps.payments.schemas import PaymentOutputSchema
from src.apps.payments.services import get_all_payments, create_payment, fulfill_payment
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_properties.conftest import db_properties
from tests.test_addresses.conftest import db_addresses
from tests.test_companies.conftest import db_companies
from tests.test_leases.conftest import db_leases
from src.apps.leases.schemas import LeaseOutputSchema
from src.apps.properties.schemas import PropertyOutputSchema
from src.apps.users.schemas import UserOutputSchema
from tests.test_users.conftest import (
    auth_headers,
    db_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)
from src.core.utils.orm import if_exists
from src.apps.users.models import User
from src.apps.properties.models import Property
from src.apps.leases.models import Lease


async def get_stripe_session_data(
    payment: PaymentOutputSchema
) -> dict[str, Any]:
    STRIPE_SESSION_DATA = {
        "id": "cs_test_id",
        "object": "checkout.session",
        "metadata": {
                    "tenant_id": payment.tenant.id, "lease_id": payment.lease.id, "payment_id": payment.id
                },
        "mode": "payment",
        "payment_method_types": ["card"],
        "payment_status": "paid",
    }
    return STRIPE_SESSION_DATA


async def get_payment_intent_data(
    lease: Lease
) -> dict[str, Any]:   
    PAYMENT_INTENT_DATA = {
    "id": "test_payment_intent_id",
    "object": "payment_intent",
    "amount": int(lease.rent_amount * 100),
    "latest_charge": "cs_2345erfw34r43r34",
    }
    return PAYMENT_INTENT_DATA



@pytest_asyncio.fixture
async def db_payments(
    async_session: Session,
    db_properties: PagedResponseSchema[PropertyOutputSchema],
    db_leases: PagedResponseSchema[LeaseOutputSchema],
    db_staff_user: UserOutputSchema,
    db_superuser: UserOutputSchema,
    db_user: UserOutputSchema
) -> PagedResponseSchema[PaymentOutputSchema]:
    lease = await if_exists(Lease, "id", db_leases.results[0].id, async_session)
    payment = await create_payment(async_session, lease, BackgroundTasks())
    stripe_session = await get_stripe_session_data(payment)
    payment_intent = await get_payment_intent_data(lease)
    await fulfill_payment(async_session, stripe_session, payment_intent, BackgroundTasks())
    
    return await get_all_payments(async_session, PageParams(), output_schema=PaymentOutputSchema)