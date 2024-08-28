from enum import Enum
import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from src.apps.leases.enums import BillingPeriodEnum
from src.apps.users.schemas import UserInfoOutputSchema
from src.apps.properties.schemas import PropertyBasicOutputSchema


class LeaseBaseSchema(BaseModel):
    start_date: datetime.date
    end_date: Optional[datetime.date]
    rent_amount: Decimal = Field(ge=0)
    inital_deposit_amount: Optional[Decimal] = Field(ge=0)
    billing_period: BillingPeriodEnum
    payment_bank_account: str

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
    inital_deposit_amount: Optional[Decimal] = Field(ge=0)

    class Config:
        orm_mode = True


class LeaseBasicOutputSchema(LeaseBaseSchema):
    id: str

    class Config:
        orm_mode = True


class LeaseOutputSchema(LeaseBasicOutputSchema):
    renewal_accepted: bool
    lease_expired: bool
    owner_id: Optional[str]
    owner: Optional[UserInfoOutputSchema]
    tenant_id: Optional[str]
    tenant: Optional[UserInfoOutputSchema]
    property_id: Optional[str]
    property: Optional[PropertyBasicOutputSchema]

    class Config:
        orm_mode = True
