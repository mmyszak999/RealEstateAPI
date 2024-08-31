import random
from decimal import Decimal

from faker import Faker
from faker.providers import address, date_time, internet, lorem, misc, person, phone_number, bank
from faker_commerce import Provider as commerce_provider
from src.apps.properties.enums import PropertyStatusEnum, PropertyTypeEnum
from src.apps.leases.enums import BillingPeriodEnum


def initialize_faker():
    faker = Faker("en_US")
    faker.seed_instance(random.randint(1, 1000))
    faker.add_provider(person)
    faker.add_provider(internet)
    faker.add_provider(date_time)
    faker.add_provider(misc)
    faker.add_provider(commerce_provider)
    faker.add_provider(address)
    faker.add_provider(lorem)
    faker.add_provider(bank)
    faker.add_provider(phone_number)

    return faker


def set_random_foundation_year() -> int:
    return random.randint(1900, 2024)


def set_random_property_value() -> int:
    return random.randint(10000, 10000000)


def set_random_rooms_amount() -> int:
    return random.randint(1, 5)


def set_random_square_meter_amount() -> int:
    return random.randint(30, 500)


def set_random_property_status() -> PropertyStatusEnum:
    return random.choice(PropertyStatusEnum.list_values())


def set_random_property_type() -> PropertyTypeEnum:
    return random.choice(PropertyTypeEnum.list_values())


def set_random_billing_period() -> PropertyTypeEnum:
    return random.choice(BillingPeriodEnum.list_values())


def set_random_rent_amount() -> int:
    return random.randint(1000, 10000)


def set_random_initial_deposit_amount() -> int:
    return random.randint(500, 5000)

