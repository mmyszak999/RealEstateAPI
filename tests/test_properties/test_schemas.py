import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic.error_wrappers import ValidationError

from src.apps.users.schemas import UserOutputSchema
from src.core.factory.property_factory import (
    PropertyInputSchemaFactory,
    PropertyUpdateSchemaFactory,
)
from tests.test_users.conftest import db_user



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


@pytest.mark.asyncio
async def test_raise_validation_error_when_updating_property_and_entered_incorrect_property_status(
    db_user: UserOutputSchema
):
    with pytest.raises(ValidationError):
        PropertyUpdateSchemaFactory().generate(property_status="no_such_status")


@pytest.mark.asyncio
async def test_raise_validation_error_when_updating_property_and_entered_incorrect_property_type(
    db_user: UserOutputSchema
):
    with pytest.raises(ValidationError):
        PropertyUpdateSchemaFactory().generate(property_type="no_such_type")