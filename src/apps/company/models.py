import datetime as dt

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class Company(Base):
    __tablename__ = "company"
    id = Column(
        String(length=50),
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    company_name = Column(String(length=100), nullable=False)
    foundation_year = Column(Integer, nullable=False)
    phone_number = Column(String(length=50), nullable=False)
    users = relationship("User", back_populates="company", lazy="selectin")
    
