from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.properties.schemas import PropertyInputSchema, PropertyUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import (
    set_random_property_status,
    set_random_property_type,
    PropertyStatusEnum,
    PropertyTypeEnum,
    set_random_foundation_year,
    set_random_square_meter_amount,
    set_random_rooms_amount,
    set_random_property_value
)



class PropertyInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=PropertyInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        property_type: PropertyTypeEnum = None,
        property_status: PropertyStatusEnum = None,
        short_description: str = None,
        square_meter: Decimal = None,
        rooms_amount: Optional[int] = None,
        year_built: Optional[int] = None,
        owner_id: Optional[str] = None,
        description: Optional[str]  = None,
        property_value: Decimal = None
    ):
        return self.schema_class(
            property_status=property_status or set_random_property_status(),
            property_type=property_type or set_random_property_type(),
            short_description=short_description or self.faker.sentence(),
            square_meter=square_meter or set_random_square_meter_amount(),
            rooms_amount=rooms_amount or set_random_rooms_amount(),
            year_built=year_built or set_random_foundation_year(),
            owner_id=owner_id,
            description=description or self.faker.sentence(),
            property_value=property_value or set_random_property_value()
        )


class PropertyUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=PropertyUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        property_type: PropertyTypeEnum = None,
        property_status: PropertyStatusEnum = None,
        short_description: str = None,
        square_meter: Decimal = None,
        rooms_amount: Optional[int] = None,
        description: Optional[str]  = None,
        property_value: Decimal = None
    ):
        return self.schema_class(
            property_status=property_status,
            property_type=property_type,
            short_description=short_description,
            rooms_amount=rooms_amount,
            description=description,
            property_value=property_value,
        )