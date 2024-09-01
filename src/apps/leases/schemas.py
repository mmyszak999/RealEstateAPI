from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from freezegun.api import FakeDate
from pydantic import BaseModel, EmailStr, Field, validator

from src.apps.leases.enums import BillingPeriodEnum
from src.apps.properties.schemas import PropertyBasicOutputSchema
from src.apps.users.schemas import UserInfoOutputSchema


class LeaseBaseSchema(BaseModel):
    start_date: date
    end_date: Optional[date]
    rent_amount: Decimal = Field(ge=0)
    initial_deposit_amount: Decimal = Field(ge=0)
    billing_period: BillingPeriodEnum
    payment_bank_account: str

    @validator("start_date")
    def validate_start_date(cls, start_date: date) -> date:
        print(isinstance(start_date, date), isinstance(start_date, FakeDate))
        if isinstance(start_date, date) and (not isinstance(start_date, FakeDate)):
            if start_date < date.today():
                raise ValueError("Start date must be in the future!")
        return start_date

    @validator("end_date")
    def validate_end_date(cls, end_date: Optional[date]) -> Optional[date]:
        print(isinstance(end_date, date), isinstance(end_date, FakeDate))
        if end_date and (isinstance(end_date, date)) and (not isinstance(end_date, FakeDate)):
            if end_date < date.today():
                raise ValueError("End date must be in the future!")
        return end_date

    class Config:
        orm_mode = True


class LeaseInputSchema(LeaseBaseSchema):
    owner_id: str
    tenant_id: str
    property_id: str

    class Config:
        orm_mode = True


class LeaseUpdateSchema(BaseModel):
    rent_amount: Optional[Decimal] = Field(ge=0)
    payment_bank_account: Optional[str]
    initial_deposit_amount: Optional[Decimal] = Field(ge=0)
    lease_expiration_date: Optional[date]

    @validator("lease_expiration_date")
    def validate_lease_expiration_date(
        cls, lease_expiration_date: Optional[date]
    ) -> Optional[date]:
        if lease_expiration_date and (lease_expiration_date < date.today()):
            raise ValueError("Lease expiration date must be in the future! ")
        return lease_expiration_date

    class Config:
        orm_mode = True


class LeaseBasicOutputSchema(LeaseBaseSchema):
    id: str
    next_payment_date: Optional[date]
    renewal_accepted: bool
    lease_expired: bool
    lease_expiration_date: Optional[date]

    class Config:
        orm_mode = True


class LeaseOutputSchema(LeaseBasicOutputSchema):
    owner_id: Optional[str]
    owner: Optional[UserInfoOutputSchema]
    tenant_id: Optional[str]
    tenant: Optional[UserInfoOutputSchema]
    property_id: Optional[str]
    property: Optional[PropertyBasicOutputSchema]

    class Config:
        orm_mode = True
