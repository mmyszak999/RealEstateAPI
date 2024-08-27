import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from src.apps.users.schemas import UserInfoOutputSchema
from src.apps.addresses.schemas import AddressBasicOutputSchema


class CompanyBaseSchema(BaseModel):
    company_name: str = Field(max_length=100)
    foundation_year: int = Field(ge=0)

    class Config:
        orm_mode = True


class CompanyInputSchema(CompanyBaseSchema):
    phone_number: str = Field(max_length=50)

    class Config:
        orm_mode = True


class CompanyUpdateSchema(BaseModel):
    company_name: Optional[str]
    foundation_year: Optional[int] = Field(ge=0)
    phone_number: Optional[str]

    class Config:
        orm_mode = True


class CompanyBasicOutputSchema(CompanyInputSchema):
    id: str
    
    class Config:
        orm_mode = True


class CompanyOutputSchema(CompanyBasicOutputSchema):
    users: list[UserInfoOutputSchema] = []
    address: Optional[AddressBasicOutputSchema] = []

    class Config:
        orm_mode = True