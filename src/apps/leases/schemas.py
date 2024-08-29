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
    initial_deposit_amount: Decimal = Field(ge=0)
    billing_period: BillingPeriodEnum
    payment_bank_account: str
    
    @validator("start_date")
    def validate_start_date(cls, start_date: datetime.date) -> datetime.date:
        if start_date < datetime.date.today():
            raise ValueError("Start date must be in the future! ")
        return start_date
    
    @validator("end_date")
    def validate_end_date(cls, end_date: Optional[datetime.date]) -> Optional[datetime.date]:
        if end_date and (end_date < datetime.date.today()):
            raise ValueError("End date must be in the past! ")
        return end_date

    class Config:
        orm_mode = True


class LeaseInputSchema(LeaseBaseSchema):
    owner_id: str
    tenant_id: str
    property_id: str
    lease_expiration_date: Optional[datetime.date]
    
    @validator("lease_expiration_date")
    def validate_lease_expiration_date(cls, lease_expiration_date: Optional[datetime.date]) -> Optional[datetime.date]:
        if lease_expiration_date and (lease_expiration_date < datetime.date.today()):
            raise ValueError("Lease expiration date must be in the future! ")
        return lease_expiration_date

    class Config:
        orm_mode = True


class LeaseUpdateSchema(BaseModel):
    rent_amount: Optional[Decimal] = Field(ge=0)
    payment_bank_account: Optional[str]
    initial_deposit_amount: Optional[Decimal] = Field(ge=0)
    lease_expiration_date: Optional[datetime.date]

    class Config:
        orm_mode = True


class LeaseBasicOutputSchema(LeaseBaseSchema):
    id: str

    class Config:
        orm_mode = True


class LeaseOutputSchema(LeaseBasicOutputSchema):
    renewal_accepted: bool
    lease_expired: bool
    lease_expiration_date: datetime.date
    owner_id: Optional[str]
    owner: Optional[UserInfoOutputSchema]
    tenant_id: Optional[str]
    tenant: Optional[UserInfoOutputSchema]
    property_id: Optional[str]
    property: Optional[PropertyBasicOutputSchema]

    class Config:
        orm_mode = True
