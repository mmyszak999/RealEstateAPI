import asyncio
from fastapi import BackgroundTasks

from src.database.db_connection import async_session

from src.core.factory.user_factory import UserRegisterSchemaFactory
from src.core.factory.company_factory import CompanyInputSchemaFactory
from src.core.factory.property_factory import PropertyInputSchemaFactory
from src.core.factory.address_factory import AddressInputSchemaFactory
from src.apps.addresses.services import create_address

from src.core.factory.lease_factory import LeaseInputSchemaFactory
from src.apps.leases.services import create_lease
from src.apps.properties.services import get_all_properties
from src.core.pagination.models import PageParams
from src.apps.properties.schemas import PropertyOutputSchema
from src.apps.leases.enums import BillingPeriodEnum



from src.apps.properties.services import (
    create_property,
    change_property_owner,
)

from src.apps.users.services.user_services import (
    create_single_user,
    create_role,
    set_user_role,
)
from src.apps.users.schemas import RoleInputSchema, UserIdSchema

from src.apps.companies.services import (
    create_company,
    add_single_user_to_company,
)


# ---------------------------------------------------------
# Roles
# ---------------------------------------------------------

async def seed_roles(session):
    roles = {
        "staff": "Internal staff member with elevated permissions",
        "user": "Regular end-user with basic access",
    }

    created = {}

    for name, description in roles.items():
        role = await create_role(
            session,
            RoleInputSchema(name=name, description=description),
        )
        created[name] = role

    return created


# ---------------------------------------------------------
# Companies
# ---------------------------------------------------------

async def seed_companies(session):
    factory = CompanyInputSchemaFactory()
    companies = []

    for _ in range(3):
        schema = factory.generate()
        company = await create_company(session, schema)
        companies.append(company)

    return companies


# ---------------------------------------------------------
# Users
# ---------------------------------------------------------

async def seed_users(session, companies):
    user_factory = UserRegisterSchemaFactory()
    staff_users = []

    # tworzymy staff users i przypisujemy do firm (bezpiecznie)
    for company in companies[:2]:
        schema = user_factory.generate()
        user = await create_single_user(session, schema, BackgroundTasks())
        user = await set_user_role(session, user.id, "staff")

        staff_users.append(user)

        await add_single_user_to_company(
            session,
            UserIdSchema(id=user.id),
            company.id,
        )

    # zwykli użytkownicy (bez firmy)
    for _ in range(3):
        schema = user_factory.generate()
        await create_single_user(session, schema, BackgroundTasks())

    return staff_users


# ---------------------------------------------------------
# Properties
# ---------------------------------------------------------

async def seed_properties(session, staff_users):
    factory = PropertyInputSchemaFactory()
    properties = []

    for _ in range(5):
        schema = factory.generate()
        prop = await create_property(session, schema)
        properties.append(prop)

    # przypisanie ownerów – jak w testach
    if staff_users and properties:
        await change_property_owner(
            session,
            UserIdSchema(id=staff_users[0].id),
            properties[0].id,
        )

        if len(staff_users) > 1 and len(properties) > 1:
            await change_property_owner(
                session,
                UserIdSchema(id=staff_users[1].id),
                properties[1].id,
            )

    return properties


async def seed_addresses(session, companies, properties):
    factory = AddressInputSchemaFactory()
    addresses = []

    for company in companies[:-1]:
        schema = factory.generate(company_id=company.id)
        address = await create_address(session, schema)
        addresses.append(address)

    for prop in properties[:-1]:
        schema = factory.generate(property_id=prop.id)
        address = await create_address(session, schema)
        addresses.append(address)

    return addresses


# ---------------------------------------------------------
# Main seed
# ---------------------------------------------------------

async def seed_data():
    async with async_session() as session:
        await seed_roles(session)

        companies = await seed_companies(session)
        staff_users = await seed_users(session, companies)
        properties = await seed_properties(session, staff_users)

        await seed_addresses(session, companies, properties)

async def seed_leases(session, staff_users, superuser):
    # bierzemy tylko dostępne nieruchomości
    available_properties = await get_all_properties(
        session,
        PageParams(),
        get_available=True,
        output_schema=PropertyOutputSchema,
    )

    # property należące do staff usera
    staff_properties = [
        prop
        for prop in available_properties.results
        if prop.owner_id == staff_users[0].id
    ]

    if not staff_properties:
        return []

    property_ = staff_properties[0]

    lease_factory = LeaseInputSchemaFactory()

    lease_schema = lease_factory.generate(
        property_id=property_.id,
        owner_id=property_.owner_id,
        tenant_id=superuser.id,
        billing_period=BillingPeriodEnum.MONTHLY,
    )

    lease = await create_lease(session, lease_schema)

    return [lease]


if __name__ == "__main__":
    asyncio.run(seed_data())
