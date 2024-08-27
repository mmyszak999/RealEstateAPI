from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.addresses.schemas import AddressInputSchema, AddressUpdateSchema
from src.core.factory.core import SchemaFactory


class AddressInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=AddressInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        country: str = None,
        state: str = None,
        city: str = None,
        postal_code: str = None,
        street: str = None,
        house_number: str = None,
        apartment_number: str = None,
        property_id: str = None,
        company_id: str = None
    ):
        return self.schema_class(
            country=country or self.faker.country(),
            state=state or self.faker.state(),
            city=city or self.faker.city(),
            postal_code=postal_code or self.faker.postcode(),
            street=street or self.faker.street_name(),
            house_number=house_number or self.faker.building_number(),
            apartment_number=apartment_number or self.faker.building_number(),
            company_id=company_id,
            property_id=property_id
        )

class AddressUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=AddressUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        country: str = None,
        state: str = None,
        city: str = None,
        postal_code: str = None,
        street: str = None,
        house_number: str = None,
        apartment_number: str = None
    ):
        return self.schema_class(
            country=country,
            state=state,
            city=city,
            postal_code=postal_code,
            street=street,
            house_number=house_number,
            apartment_number=apartment_number
        )