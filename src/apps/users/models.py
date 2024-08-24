import datetime as dt

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class User(Base):
    __tablename__ = "user"
    id = Column(
        String(length=50),
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=75), nullable=False)
    email = Column(String(length=100), unique=True, nullable=False)
    password = Column(String(length=60), nullable=True)
    birth_date = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
    is_staff = Column(Boolean, nullable=False, default=False)
    phone_number = Column(String(length=50), nullable=False)
    created_at = Column(DateTime, default=dt.datetime.now, nullable=True)
