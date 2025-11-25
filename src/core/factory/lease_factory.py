from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from src.apps.leases.enums import BillingPeriodEnum
from src.apps.leases.schemas import LeaseInputSchema, LeaseUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import (
    set_random_billing_period,
    set_random_initial_deposit_amount,
    set_random_rent_amount,
)
from src.core.utils.time import generate_random_date


class LeaseInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=LeaseInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        start_date: date = None,
        end_date: date = None,
        rent_amount: Decimal = None,
        initial_deposit_amount: Decimal = None,
        billing_period: BillingPeriodEnum = None,
        payment_bank_account: str = None,
        owner_id: str = None,
        tenant_id: str = None,
        property_id: str = None,
    ):
        today = date.today()

        start_date_range_start = today - timedelta(days=3)
        start_date_range_end = today + timedelta(days=4)

        end_date_range_start = today + timedelta(days=14)
        end_date_range_end = today + timedelta(days=30)

        return self.schema_class(
            start_date=start_date
            or generate_random_date(
                start_date=start_date_range_start,
                end_date=start_date_range_end,
            ),
            end_date=end_date
            or generate_random_date(
                start_date=end_date_range_start,
                end_date=end_date_range_end,
            ),
            rent_amount=rent_amount or set_random_rent_amount(),
            initial_deposit_amount=initial_deposit_amount
            or set_random_initial_deposit_amount(),
            billing_period=billing_period or set_random_billing_period(),
            payment_bank_account=payment_bank_account or self.faker.iban(),
            owner_id=owner_id,
            tenant_id=tenant_id,
            property_id=property_id,
        )


class LeaseUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=LeaseUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        rent_amount: Optional[Decimal] = None,
        initial_deposit_amount: Optional[Decimal] = None,
        lease_expiration_date: Optional[date] = None,
        payment_bank_account: Optional[str] = None,
    ):
        return self.schema_class(
            rent_amount=rent_amount,
            initial_deposit_amount=initial_deposit_amount,
            lease_expiration_date=lease_expiration_date,
            payment_bank_account=payment_bank_account,
        )
