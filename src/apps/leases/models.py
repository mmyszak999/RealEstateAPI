import datetime as dt
from decimal import Decimal

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy import Enum as SQLAlchemyEnum

from src.apps.leases.enums import BillingPeriodEnum

from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class Lease(Base):
    __tablename__ = "lease"
    id = Column(
        String(length=50),
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    rent_amount = Column(DECIMAL, nullable=False)
    initial_deposit_amount = Column(DECIMAL, nullable=True, default=Decimal(0))
    renewal_accepted = Column(Boolean, nullable=False, default=False)
    lease_expired = Column(Boolean, nullable=False, default=False)
    lease_expiration_date = Column(Date, nullable=True)
    billing_period = Column(
        SQLAlchemyEnum(BillingPeriodEnum),
        nullable=False,
        default=BillingPeriodEnum.MONTHLY
    )
    payment_bank_account = Column(String(length=75), nullable=False)
    tenant = relationship("User", back_populates="tenant_leases", lazy="joined")
    tenant_id = Column(
        String(length=50),
        ForeignKey("user.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=False,
    )
    owner = relationship("User", back_populates="owner_leases", lazy="joined")
    owner_id = Column(
        String(length=50),
        ForeignKey("user.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=False,
    )
    property = relationship("Property", back_populates="leases", lazy="joined")
    property_id = Column(
        String(length=50),
        ForeignKey("property.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=False,
    )
    
