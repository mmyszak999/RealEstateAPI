import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from src.apps.users.schemas import UserInfoOutputSchema


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
    users: Optional[list[UserInfoOutputSchema]] = []

    class Config:
        orm_mode = True


class CompanyIdSchema(BaseModel):
    id: str
    
    class Config:
        orm_mode = True
