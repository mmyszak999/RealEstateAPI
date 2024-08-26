from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def list_values(cls):
        return [member.value for member in cls]

    @classmethod
    def list_names(cls):
        return [member.name for member in cls]


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