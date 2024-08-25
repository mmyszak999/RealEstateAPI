from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.users.schemas import UserRegisterSchema, UserPasswordSchema, UserUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.time import set_employment_date_for_factory


class UserRegisterSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=UserRegisterSchema):
        super().__init__(schema_class)

    def generate(
        self,
        email: str = None,
        first_name: str = None,
        last_name: str = None,
        birth_date: date = None,
        phone_number: str = None,
        password: str = "password",
        password_repeat: str = "password",
    ):
        return self.schema_class(
            first_name=first_name or self.faker.first_name(),
            last_name=last_name or self.faker.last_name(),
            email=email or self.faker.ascii_email(),
            birth_date=birth_date or self.faker.date_of_birth(),
            phone_number=phone_number or self.faker.phone_number(),
            password=password,
            password_repeat=password_repeat,
        )


class UserUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=UserUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        birth_date: Optional[date] = None,
        phone_number: Optional[str] = None
    ):
        return self.schema_class(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            birth_date=birth_date
        )
