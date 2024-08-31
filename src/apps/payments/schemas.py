from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from src.apps.users.schemas import UserInfoOutputSchema, UserOutputSchema
from src.apps.leases.schemas import LeaseBasicOutputSchema


class PaymentBaseOutputSchema(BaseModel):
    id: str
    amount: Optional[Decimal]
    tenant: UserOutputSchema
    payment_date: Optional[date]
    created_at: Optional[date]
    payment_accepted: bool
    waiting_for_payment: bool
    

class PaymentOutputSchema(PaymentBaseOutputSchema):
    stripe_charge_id: Optional[str]
    lease: LeaseBasicOutputSchema

    class Config:
        orm_mode = True



class PaymentAwaitSchema(BaseModel):
    lease_id: str
    payment_id: str
    tenant_id: str
    rent_amount: str
    created_at: str
    
    
class PaymentConfirmationSchema(PaymentAwaitSchema):
    pass


class StripePublishableKeySchema(BaseModel):
    publishable_key: str
    

class StripeSessionSchema(BaseModel):
    session_id: str
    url: str