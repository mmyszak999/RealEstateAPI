from decimal import Decimal
from typing import Any


class ServiceException(Exception):
    pass


class DoesNotExist(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{class_name} with {field}={value} does not exist")


class AlreadyExists(ServiceException):
    def __init__(
        self, class_name: str, field: str, value: Any, comment: str = ""
    ) -> None:
        super().__init__(f"{class_name} with {field}={value} already exists {comment}")


class IsOccupied(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{field}={value} value of {class_name} is occupied")


class AuthenticationException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class AuthorizationException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class AccountNotActivatedException(ServiceException):
    def __init__(self, field: str, value: Any) -> None:
        super().__init__(
            f"The account of the user with {field}={value} has not been activated! "
            "Please check your mailbox to find the message with activation link. "
            "If you think this is a mistake, contact or mail our support team!"
        )


class AccountAlreadyDeactivatedException(ServiceException):
    def __init__(self, field: str, value: Any) -> None:
        super().__init__(
            f"The account of the user with {field}={value} was already deactivated!"
        )


class AccountAlreadyActivatedException(ServiceException):
    def __init__(self, field: str, value: Any) -> None:
        super().__init__(
            f"The account of the user with {field}={value} was already activated!"
        )


class UserCantDeactivateTheirAccountException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"User can't deactivate their account!")


class UserCantActivateTheirAccountException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            "User can't activate their account by other way than using activation link when account created! "
            "If necessary, please contact our support team! "
        )


class UnavailableFilterFieldException(ServiceException):
    def __init__(self) -> None:
        super().__init__("One of the filter fields is not available for filtering! ")


class UnavailableSortFieldException(ServiceException):
    def __init__(self) -> None:
        super().__init__("One of the sort fields is not available for sorting! ")


class NoSuchFieldException(ServiceException):
    def __init__(self, model_name: str, field: str) -> None:
        super().__init__(f"Object {model_name} does not have field={field} ! ")
        
        
class OwnerAlreadyHasTheOwnershipException(ServiceException):
    def __init__(self) -> None:
        super().__init__("The owner is already assigned to the property ownership! ")
        
        
class IncorrectEnumValueException(ServiceException):
    def __init__(self, field_name: str, typed_value:any, available_values: list[any]) -> None:
        super().__init__(
            f"The value for the field {field_name}={typed_value} is incorrect! "
            f"Pick from available values: {available_values}"
        )

class UserAlreadyHasCompanyException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"User already belongs to the other company! ")
    

