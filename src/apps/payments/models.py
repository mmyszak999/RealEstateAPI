import datetime as dt
from decimal import Decimal

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.apps.leases.enums import BillingPeriodEnum
from src.core.utils.orm import (
    default_lease_expiration_date,
    default_next_payment_date
)
from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class Payment(Base):
    __tablename__ = "payment"
    id = Column(
        String(length=50), primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    stripe_charge_id = Column(String(length=300), nullable=True)
    amount = Column(DECIMAL, nullable=True)
    created_at = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=True)
    waiting_for_payment = Column(Boolean, nullable=False, default=True)
    payment_accepted = Column(Boolean, nullable=False, default=False)
    payment_checkout_url = Column(String(length=500), nullable=True)
    lease_id = Column(
        String(length=50),
        ForeignKey("lease.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )
    lease = relationship("Lease", back_populates="payments")
    tenant_id = Column(
        String(length=50),
        ForeignKey("user.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True
    )
    tenant = relationship("User", back_populates="payments")