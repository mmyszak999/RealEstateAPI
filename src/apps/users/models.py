import datetime as dt

from sqlalchemy import Boolean, Column, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base
from src.apps.properties.models import Property


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
    phone_number = Column(String(length=50), nullable=False)
    created_at = Column(DateTime, default=dt.datetime.now, nullable=True)

    # Relationships
    properties = relationship("Property", back_populates="owner", lazy="joined")
    company_id = Column(
        String(length=50),
        ForeignKey("company.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )
    company = relationship("Company", back_populates="users", lazy="joined")

    owner_leases = relationship(
        "Lease", back_populates="owner", lazy="joined", foreign_keys="Lease.owner_id"
    )
    tenant_leases = relationship(
        "Lease", back_populates="tenant", lazy="joined", foreign_keys="Lease.tenant_id"
    )
    payments = relationship("Payment", back_populates="tenant", lazy="joined")

    role_id = Column(
        String(length=50),
        ForeignKey("role.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )

    role = relationship("Role", back_populates="users", lazy="joined")


class Role(Base):
    __tablename__ = "role"

    id = Column(
        String(50),
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    users = relationship("User", back_populates="role", lazy="joined")
