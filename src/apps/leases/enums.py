from src.core.utils.enums import BaseEnum


class BillingPeriodEnum(BaseEnum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class PropertyStatusEnum(BaseEnum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    RENTED = "RENTED"
    RESERVED = "RESERVED"