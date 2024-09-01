from datetime import date, timedelta

import pytest
from pydantic.error_wrappers import ValidationError

from src.core.factory.lease_factory import LeaseInputSchemaFactory
from src.apps.leases.schemas import LeaseInputSchema
from src.core.utils.utils import generate_uuid


@pytest.mark.asyncio
async def test_raise_validation_error_when_creating_lease_and_entered_incorrect_billing_period():
    with pytest.raises(ValidationError):
        LeaseInputSchemaFactory().generate(
            billing_period="no_such_billing_period",
            property_id=generate_uuid(),
            owner_id=generate_uuid(),
            tenant_id=generate_uuid(),
        )


@pytest.mark.asyncio
async def test_raise_value_error_when_creating_lease_and_entered_past_start_date():
    with pytest.raises(ValueError):
        LeaseInputSchema(
            start_date=date(1333,12,2),
            property_id=generate_uuid(),
            owner_id=generate_uuid(),
            tenant_id=generate_uuid(),
        )


@pytest.mark.asyncio
async def test_raise_value_error_when_creating_lease_and_entered_past_end_date():
    with pytest.raises(ValueError):
        LeaseInputSchema(
            start_date=date(3333,12,2),
            end_date=date(1333,12,2),
            property_id=generate_uuid(),
            owner_id=generate_uuid(),
            tenant_id=generate_uuid(),
        )
