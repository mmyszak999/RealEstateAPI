import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from src.apps.users.schemas import UserInfoOutputSchema


class AddressBaseSchema(BaseModel):
    country: str
    state: Optional[str]
    city: str
    postal_code: str
    street: Optional[str]
    house_number: str
    apartment_number: Optional[str]
    company_id: Optional[str]
    property_id: Optional[str]


class AddressInputSchema(AddressBaseSchema):
    pass

    class Config:
        orm_mode = True


class AddressUpdateSchema(BaseModel):
    country: Optional[str]
    state: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    street: Optional[str]
    house_number: Optional[str]
    apartment_number: Optional[str]


class AddressOutputSchema(AddressBaseSchema):
    id: str

    class Config:
        orm_mode = True