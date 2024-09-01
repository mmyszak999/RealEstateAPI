import datetime

import pytest
from fastapi import BackgroundTasks, status
from fastapi_jwt_auth import AuthJWT
from freezegun import freeze_time
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.leases.enums import BillingPeriodEnum
from src.apps.leases.models import Lease
from src.apps.leases.schemas import LeaseOutputSchema
from src.apps.leases.services import (
    create_lease,
    manage_leases_with_incoming_payment_date,
)
from src.apps.payments.models import Payment
from src.apps.payments.schemas import PaymentOutputSchema
from src.apps.payments.services import (
    create_payment,
    fulfill_payment,
    get_all_payments,
    get_single_payment,
)
from src.apps.properties.models import Property
from src.apps.properties.schemas import PropertyOutputSchema
from src.apps.users.models import User
from src.apps.users.schemas import UserOutputSchema
from src.core.exceptions import (
    AccountNotActivatedException,
    AlreadyExists,
    AuthenticationException,
    DoesNotExist,
    PaymentAlreadyAccepted,
    ServiceException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import get_billing_period_time_span_between_payments, if_exists
from src.core.utils.utils import generate_uuid
from tests.test_addresses.conftest import db_addresses
from tests.test_companies.conftest import db_companies
from tests.test_leases.conftest import db_leases
from tests.test_payments.conftest import (
    db_payments,
    get_payment_intent_data,
    get_stripe_session_data,
)
from tests.test_properties.conftest import db_properties
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    auth_headers,
    db_staff_user,
    db_superuser,
    db_user,
    staff_auth_headers,
)


@pytest.mark.asyncio
async def test_if_lease_with_payment_date_being_today_was_managed_correctly_while_creating_payment(
    async_session: AsyncSession, db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    lease_before = db_leases.results[0]

    with freeze_time(lease_before.next_payment_date):
        await manage_leases_with_incoming_payment_date(async_session, BackgroundTasks())
        lease_after = await if_exists(
            Lease, "id", db_leases.results[0].id, async_session
        )
        _, time_span = get_billing_period_time_span_between_payments(
            lease_before.next_payment_date, lease_before.billing_period
        )

        assert lease_after.next_payment_date == (
            lease_before.next_payment_date + datetime.timedelta(days=time_span)
        )


@pytest.mark.asyncio
async def test_if_single_payment_was_returned(
    async_session: AsyncSession, db_payments: PagedResponseSchema[PaymentOutputSchema]
):
    payment = await get_single_payment(async_session, db_payments.results[0].id)

    assert payment.id == db_payments.results[0].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_payment(
    async_session: AsyncSession, db_payments: PagedResponseSchema[PaymentOutputSchema]
):
    with pytest.raises(DoesNotExist):
        await get_single_payment(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_payments_were_returned(
    async_session: AsyncSession, db_payments: PagedResponseSchema[PaymentOutputSchema]
):
    payments = await get_all_payments(async_session, PageParams())
    assert payments.total == 1


@pytest.mark.asyncio
async def test_specific_payments_will_returned_depending_on_the_filter_key(
    async_session: AsyncSession,
    db_payments: PagedResponseSchema[PaymentOutputSchema],
    db_staff_user: UserOutputSchema,
    db_superuser: UserOutputSchema,
):
    accepted_payments = await get_all_payments(
        async_session, PageParams(), get_accepted=True
    )
    assert accepted_payments.total == 1

    waiting_payments = await get_all_payments(
        async_session, PageParams(), get_waiting=True
    )
    assert waiting_payments.total == 0

    superuser_payments = await get_all_payments(
        async_session, PageParams(), tenant_id=db_superuser.id
    )
    assert superuser_payments.total == 1

    staff_user_payments = await get_all_payments(
        async_session, PageParams(), tenant_id=db_staff_user.id
    )
    assert staff_user_payments.total == 0


@pytest.mark.asyncio
async def test_raise_exception_while_fulfilling_nonexistent_payment(
    async_session: AsyncSession, db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    lease = await if_exists(Lease, "id", db_leases.results[0].id, async_session)
    payment = await create_payment(async_session, lease, BackgroundTasks())
    stripe_session = await get_stripe_session_data(payment)
    payment_intent = await get_payment_intent_data(lease)
    stripe_session["metadata"]["payment_id"] = "no_such_payment"

    with pytest.raises(DoesNotExist):
        await fulfill_payment(
            async_session, stripe_session, payment_intent, BackgroundTasks()
        )


@pytest.mark.asyncio
async def test_raise_exception_while_fulfilling_accepted_payment(
    async_session: AsyncSession, db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    lease = await if_exists(Lease, "id", db_leases.results[0].id, async_session)
    payment = await create_payment(async_session, lease, BackgroundTasks())
    stripe_session = await get_stripe_session_data(payment)
    payment_intent = await get_payment_intent_data(lease)

    await fulfill_payment(
        async_session, stripe_session, payment_intent, BackgroundTasks()
    )

    with pytest.raises(PaymentAlreadyAccepted):
        await fulfill_payment(
            async_session, stripe_session, payment_intent, BackgroundTasks()
        )


@pytest.mark.asyncio
async def test_if_payment_was_fulfilled_correctly(
    async_session: AsyncSession, db_leases: PagedResponseSchema[LeaseOutputSchema]
):
    lease = await if_exists(Lease, "id", db_leases.results[0].id, async_session)

    with freeze_time(lease.next_payment_date + datetime.timedelta(days=1)):
        payment_before = await create_payment(async_session, lease, BackgroundTasks())

        assert payment_before.stripe_charge_id == None
        assert payment_before.amount == None
        assert payment_before.waiting_for_payment == True
        assert payment_before.payment_accepted == False
        assert payment_before.payment_date == None

        stripe_session = await get_stripe_session_data(payment_before)
        payment_intent = await get_payment_intent_data(lease)

        await fulfill_payment(
            async_session, stripe_session, payment_intent, BackgroundTasks()
        )

        payment_after = await if_exists(Payment, "id", payment_before.id, async_session)
        assert payment_after.stripe_charge_id is not None
        assert payment_after.amount == lease.rent_amount
        assert payment_after.waiting_for_payment == False
        assert payment_after.payment_accepted == True
        assert payment_after.payment_date == datetime.date.today()
