from enum import Enum
import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from src.apps.properties.enums import PropertyTypeEnum, PropertyStatusEnum
from src.apps.users.schemas import UserInfoOutputSchema, UserIdSchema
from src.apps.addresses.schemas import AddressBasicOutputSchema


class PropertyBaseSchema(BaseModel):
    property_type: PropertyTypeEnum
    property_status: PropertyStatusEnum
    short_description: str = Field(max_length=100)
    square_meter: Decimal
    rooms_amount: Optional[int] = Field(ge=0)
    year_built: Optional[int] = Field(ge=0)

    class Config:
        orm_mode = True


class PropertyInputSchema(PropertyBaseSchema):
    owner_id: Optional[str]
    description: Optional[str] = Field(max_length=500)
    property_value: Decimal
    
    class Config:
        orm_mode = True


class PropertyUpdateSchema(BaseModel):
    property_type: Optional[PropertyTypeEnum]
    short_description: Optional[str]
    description: Optional[str]
    property_value: Optional[Decimal]
    square_meter: Optional[Decimal]
    rooms_amount: Optional[Decimal]
    property_status: Optional[PropertyStatusEnum]

    class Config:
        orm_mode = True


class PropertyBasicOutputSchema(PropertyBaseSchema):
    id: str

    class Config:
        orm_mode = True


class PropertyOutputSchema(PropertyBasicOutputSchema):
    owner_id: Optional[str]
    owner: Optional[UserInfoOutputSchema]
    description: Optional[str]
    property_value: Decimal
    created_at: Optional[datetime.datetime]
    address: Optional[AddressBasicOutputSchema] = []

    class Config:
        orm_mode = True


class PropertyOwnerIdSchema(UserIdSchema):
    pass
