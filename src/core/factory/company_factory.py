from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.companies.schemas import CompanyInputSchema, CompanyUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_random_foundation_year


class CompanyInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=CompanyInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        company_name: str = None,
        foundation_year: str = None,
        phone_number: str = None
    ):
        return self.schema_class(
            company_name=company_name or self.faker.ecommerce_name(),
            foundation_year=foundation_year or set_random_foundation_year(),
            phone_number=phone_number or self.faker.phone_number()
        )

class CompanyUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=CompanyUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        company_name: str = None,
        foundation_year: str = None,
        phone_number: str = None
    ):
        return self.schema_class(
            company_name=company_name,
            foundation_year=foundation_year,
            phone_number=phone_number
        )