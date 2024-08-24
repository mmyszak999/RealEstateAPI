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
            f"User can't activate their account by other way than using activation link when account created! "
            "If necessary, please contact our support team! "
        )


class PasswordAlreadySetException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"This account already has its password set! ")


class PasswordNotSetException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"This account hasn't got the password set! ")


class ProductIsAlreadyLegacyException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"This product is already legacy")


class LegacyProductException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            f"This product is treated as a legacy product and no action can be proceeded "
        )


class CannotRetrieveIssuedStockException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"This stock can't be retrieved as it is unavailable! ")


class MissingProductDataException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            f"Product id or product count data is not consistent or complete! "
        )


class MissingIssueDataException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"Issue create data was not provided! ")


class MissingReceptionDataException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"Reception create data was not provided! ")


class TooLittleWaitingRoomWeightException(ServiceException):
    def __init__(self, value1: Decimal, value2: Decimal) -> None:
        super().__init__(
            f"The Requested waiting room weight ({value1}) is lower than the weight of "
            f"all the stocks in the waiting room({value2}) !"
        )


class TooLittleWaitingRoomSpaceException(ServiceException):
    def __init__(self, value1: Decimal, value2: Decimal) -> None:
        super().__init__(
            f"The Requested waiting room stock slots amount ({value1}) is lower than the amount of "
            f"the stocks in the waiting room({value2}) !"
        )


class WaitingRoomIsNotEmptyException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"The waiting room with stocks inside cannot be deleted! ")


class CannotMoveIssuedStockException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"The requested stock was issued and can't be moved! ")


class StockAlreadyInWaitingRoomException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"The requested stock was already placed in a waiting room! ")


class NoAvailableSlotsInWaitingRoomException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            f"This waiting room has no more available slots to store the stocks! "
        )


class NoAvailableWeightInWaitingRoomException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            f"This waiting room has no more available weight to store the stocks! "
        )


class NoAvailableWaitingRoomsException(ServiceException):
    def __init__(
        self, product_name: Decimal, product_count: int, stock_weight: Decimal
    ) -> None:
        super().__init__(
            f"The stock can't be recepted because there is no available waiting rooms for the stock (due to lack of space/weight limit)! "
            f"Stock data: product_name: {product_name}, count: {product_count}, weight: {stock_weight} "
        )


class WarehouseAlreadyExistsException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            f"The warehouses instance already exists and the second one cannot be created!"
        )


class WarehouseDoesNotExistException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            f"The object cannot be created because the warehouse instance does not exist !"
        )


class TooLittleSectionAmountException(ServiceException):
    def __init__(self, max_sections: int, occupied_sections: int) -> None:
        super().__init__(
            f"The requested sections amount ({max_sections}) is lower than the amount of "
            f"currently occupied sections in the warehouse({occupied_sections}) !"
        )


class TooLittleWaitingRoomAmountException(ServiceException):
    def __init__(self, max_waiting_rooms: int, occupied_waiting_rooms: int) -> None:
        super().__init__(
            f"The requested waiting rooms amount ({max_waiting_rooms}) is lower than the amount of "
            f"currently occupied waiting rooms in the warehouse({occupied_waiting_rooms}) !"
        )


class WarehouseIsNotEmptyException(ServiceException):
    def __init__(self, resource: str) -> None:
        super().__init__(
            f"The warehouse cannot be deleted because it still contains not empty {resource} inside! "
        )


class SectionIsNotEmptyException(ServiceException):
    def __init__(self, resource: str) -> None:
        super().__init__(
            f"The section cannot be deleted because it is not empty! Reason: positive amount of {resource} "
        )


class NotEnoughWarehouseResourcesException(ServiceException):
    def __init__(self, resource: str) -> None:
        super().__init__(f"The warehouse can have no more {resource} !")


class TooLittleWeightAmountException(ServiceException):
    def __init__(self, value1: Decimal, value2: Decimal, model: str) -> None:
        super().__init__(
            f"The requested {model} weight amount ({value1}) is lower than the available weight of "
            f"the stocks or the reserved weight amount for the racks in the {model} ({value2}) !"
        )


class TooLittleRacksAmountException(ServiceException):
    def __init__(self, value1: int, value2: int) -> None:
        super().__init__(
            f"The requested section max racks amount ({value1}) is lower than the amount of "
            f"the racks in the section({value2}) !"
        )


class TooLittleRackLevelsAmountException(ServiceException):
    def __init__(self, value1: int, value2: int) -> None:
        super().__init__(
            f"The requested rack level amount ({value1}) is lower than the amount of "
            f"the rack levels in the rack({value2}) !"
        )


class RackIsNotEmptyException(ServiceException):
    def __init__(self, resource: str) -> None:
        super().__init__(
            f"The rack cannot be deleted because it is not empty! Reason: positive amount of {resource} "
        )


class NotEnoughSectionResourcesException(ServiceException):
    def __init__(self, resource: str, reason: str) -> None:
        super().__init__(f"The section can have no more {resource} - {reason} !")


class NotEnoughRackResourcesException(ServiceException):
    def __init__(self, resource: str, reason: str) -> None:
        super().__init__(f"The rack can have no more {resource} - {reason} !")


class WeightLimitExceededException(ServiceException):
    def __init__(self, value1: Decimal, value2: Decimal) -> None:
        super().__init__(
            f"The requested weight amount ({value1}) is higher than the available weight for "
            f"this operation at this moment ({value2}) !"
        )


class TooLittleRackLevelSlotsAmountException(ServiceException):
    def __init__(self, value1: int, value2: int) -> None:
        super().__init__(
            f"The requested rack level max slots amount ({value1}) is lower than the amount of "
            f"the slots in the rack level ({value2}) !"
        )


class RackLevelIsNotEmptyException(ServiceException):
    def __init__(self, resource: str) -> None:
        super().__init__(
            f"The rack level cannot be deleted because it is not empty! Reason: positive amount of {resource} "
        )


class NotEnoughRackLevelResourcesException(ServiceException):
    def __init__(self, resource: str, reason: str) -> None:
        super().__init__(f"The rack level can have no more {resource} - {reason} !")


class CantDeactivateRackLevelSlotException(ServiceException):
    def __init__(self, reason: str) -> None:
        super().__init__(f"The rack level slot cannot be  deactivated - {reason} !")


class CantActivateRackLevelSlotException(ServiceException):
    def __init__(self, reason: str) -> None:
        super().__init__(f"The rack level slot cannot be activated - {reason} !")


class RackLevelSlotIsNotEmptyException(ServiceException):
    def __init__(self, resource: str) -> None:
        super().__init__(
            f"The rack level slot cannot be deleted because it is not empty! Reason: {resource} "
        )


class TooSmallInactiveSlotsQuantityException(ServiceException):
    def __init__(self, inactive_slots: int) -> None:
        super().__init__(
            f"Cannot reduce the amount of the rack level slots - too small amount of inactive slots ({inactive_slots}) !"
        )


class ExistingGapBetweenInactiveSlotsToDeleteException(ServiceException):
    def __init__(self, slots_amount: int) -> None:
        super().__init__(
            f"Requested to reduce the rack level slots amount by {slots_amount}. "
            f"There is a gap between these {slots_amount} slots being removed. "
            f"Make the last {slots_amount} empty and try again!"
        )


class NoAvailableRackLevelSlotException(ServiceException):
    def __init__(
        self, product_name: Decimal, product_count: int, stock_weight: Decimal
    ) -> None:
        super().__init__(
            "The stock can't be recepted because there is no available rack level slot in the requested rack level "
            "for the new stock (due to lack of space/weight limit)! "
            f"Stock data: product_name: {product_name}, count: {product_count}, weight: {stock_weight} "
        )


class AmbiguousStockStoragePlaceDuringReceptionException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            "Stock cannot be placed on the waiting room and the rack level slot simultaneously! "
            "Please pick only one! "
        )


class StockAlreadyInRackLevelException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"The requested stock was already placed in this rack level! ")


class NoAvailableSlotsInRackLevelException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            f"This rack level has no more available slots to store the stocks! "
        )


class NoAvailableWeightInRackLevelException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            f"This rack level has no more available weight to store the stocks! "
        )


class UnavailableFilterFieldException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"One of the filter fields is not available for filtering! ")


class UnavailableSortFieldException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"One of the sort fields is not available for sorting! ")


class NoSuchFieldException(ServiceException):
    def __init__(self, model_name: str, field: str) -> None:
        super().__init__(f"Object {model_name} does not have field={field} ! ")
