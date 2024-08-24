import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserLoginInputSchema(BaseModel):
    email: EmailStr = Field()
    password: str = Field()


class UserBaseSchema(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=75)

    class Config:
        orm_mode = True


class UserInputSchema(UserBaseSchema):
    email: EmailStr = Field()
    birth_date: datetime.date
    phone_number: str = Field(max_length=50)

    @validator("birth_date")
    def validate_birth_date(cls, birth_date: datetime.date) -> datetime.date:
        if birth_date >= datetime.date.today():
            raise ValueError("Birth date must be in the past")
        return birth_date

    class Config:
        orm_mode = True


class UserPasswordSchema(BaseModel):
    password: str = Field(min_length=8, max_length=60)
    password_repeat: str = Field(min_length=8, max_length=60)

    @validator("password_repeat")
    def validate_passwords(cls, rep_password: str, values: dict[str, Any]) -> str:
        if rep_password != values["password"]:
            raise ValueError("Passwords are not identical")
        return rep_password

    class Config:
        orm_mode = True


class UserRegisterSchema(UserInputSchema, UserPasswordSchema):
    pass

    class Config:
        orm_mode = True


class UserUpdateSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    birth_date: Optional[datetime.date]
    phone_number: Optional[str]

    @validator("birth_date")
    def validate_birth_date(cls, birth_date: Optional[datetime.date]) -> Optional[datetime.date]:
        if birth_date and (birth_date >= datetime.date.today()):
            raise ValueError("Birth date must be in the past")
        return birth_date

    class Config:
        orm_mode = True


class UserInfoOutputSchema(UserBaseSchema):
    id: str
    email: EmailStr
    birth_date: datetime.date
    is_active: bool

    class Config:
        orm_mode = True


class UserOutputSchema(UserInputSchema):
    id: str
    is_active: bool
    is_superuser: bool
    is_staff: bool
    created_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True
