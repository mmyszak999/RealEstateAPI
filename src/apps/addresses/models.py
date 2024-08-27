import datetime as dt

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class Address(Base):
    __tablename__ = "address"
    id = Column(
        String(length=50),
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    country = Column(String(length=100), nullable=False)
    state = Column(String(length=50), nullable=True)
    city = Column(String(length=100), nullable=False)
    postal_code = Column(String(length=30), nullable=False)
    street = Column(String(length=100), nullable=True)
    house_number = Column(String(length=15), nullable=False)
    apartment_number = Column(String(length=10), nullable=True)
    company_id = Column(
        String(length=50),
        ForeignKey("company.id", ondelete="cascade", onupdate="cascade"),
        nullable=True,
    )
    company = relationship("Company", back_populates="address", lazy="subquery")
    property_id = Column(
        String(length=50),
        ForeignKey("property.id", ondelete="cascade", onupdate="cascade"),
        nullable=True,
    )
    property = relationship("Property", back_populates="address", lazy="subquery")
    
