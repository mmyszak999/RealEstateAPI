import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic.error_wrappers import ValidationError

from src.apps.users.schemas import UserIdSchema, UserOutputSchema
from src.apps.properties.schemas import PropertyOutputSchema, PropertyOwnerIdSchema
from src.apps.properties.services import (
    create_property,
    get_all_properties,
    get_single_property,
    update_single_property,
    change_property_owner
)
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    ServiceException,
    IncorrectEnumValueException,
    OwnerAlreadyHasTheOwnershipException
    )
from src.core.factory.property_factory import (
    PropertyInputSchemaFactory,
    PropertyUpdateSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_properties.conftest import DB_PROPERTIES_SCHEMAS, db_properties
from tests.test_users.conftest import db_staff_user, db_user
from src.core.utils.orm import if_exists
from src.apps.users.models import User


@pytest.mark.asyncio
async def test_raise_validation_error_when_creating_property_and_entered_incorrect_property_status(
    db_user: UserOutputSchema
):
    with pytest.raises(ValidationError):
        PropertyInputSchemaFactory().generate(owner_id=db_user.id, property_status="no_such_status")


@pytest.mark.asyncio
async def test_raise_validation_error_when_creating_property_and_entered_incorrect_property_type(
    db_user: UserOutputSchema
):
    with pytest.raises(ValidationError):
        PropertyInputSchemaFactory().generate(owner_id=db_user.id, property_type="no_such_type")