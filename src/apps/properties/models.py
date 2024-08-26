import datetime as dt

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class Property(Base):
    __tablename__ = "property"
    id = Column(
        String(length=50),
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    property_type = Column(String(length=50), nullable=False) #enum
    short_description = Column(String(length=100), nullable=False)
    description = Column(String(length=500), unique=True, nullable=True)
    property_value = Column(DECIMAL, nullable=False)
    square_meter = Column(DECIMAL, nullable=False)
    rooms_amount = Column(Integer, nullable=True)
    year_built = Column(Integer, nullable=True)
    property_status = Column(String(length=50), nullable=False) #enum
    owner_id = Column(
        String,
        ForeignKey("user.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=False,
    )
    owner = relationship("User", back_populates="properties", lazy="selectin")
    created_at = Column(DateTime, default=dt.datetime.now, nullable=True)
