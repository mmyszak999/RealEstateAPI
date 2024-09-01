from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def list_values(cls):
        return [member.value for member in cls]

    @classmethod
    def list_names(cls):
        return [member.name for member in cls]
