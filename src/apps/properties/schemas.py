import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class PropertyBaseSchema(BaseModel):
    property_type: str = Field(max_length=50)
    short_description: str = Field(max_length=100)
    square_meter: Decimal
    rooms_amount: Optional[int]
    year_built: Optional[int]

    class Config:
        orm_mode = True


class PropertyInputSchema(PropertyBaseSchema):
    description: Optional[str] = Field(max_length=500)
    property_value: Decimal
    
    class Config:
        orm_mode = True


class PropertyUpdateSchema(BaseModel):
    property_type: Optional[str]
    short_description: Optional[str]
    description: Optional[str]
    property_value: Optional[Decimal]
    square_meter: Optional[Decimal]
    rooms_amount: Optional[Decimal]
    property_status: Optional[str]

    class Config:
        orm_mode = True


class PropertyInfoOutputSchema(PropertyBaseSchema):
    pass

    class Config:
        orm_mode = True


class PropertyOutputSchema(PropertyInfoOutputSchema):
    id: str
    description: Optional[str]
    property_value: Decimal
    created_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True
