from src.core.utils.enums import BaseEnum


class PropertyTypeEnum(BaseEnum):
    HOUSE = "HOUSE"
    APARTMENT = "APARTMENT"
    COMMERCIAL = "COMMERCIAL"
    LAND = "LAND"


class PropertyStatusEnum(BaseEnum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    RENTED = "RENTED"
    RESERVED = "RESERVED"
