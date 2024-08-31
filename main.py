from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.middleware.cors import CORSMiddleware

from src.apps.emails.routers import email_router
from src.apps.users.routers import user_router
from src.apps.jwt.routers import jwt_router
from src.apps.properties.routers import property_router
from src.apps.companies.routers import company_router
from src.apps.addresses.routers import address_router
from src.apps.leases.routers import lease_router
from src.core.exceptions import (
    AccountAlreadyActivatedException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException,
    AlreadyExists,
    AuthenticationException,
    AuthorizationException,
    DoesNotExist,
    IsOccupied,
    ServiceException,
    UserCantActivateTheirAccountException,
    UserCantDeactivateTheirAccountException,
    NoSuchFieldException,
    UnavailableFilterFieldException,
    UnavailableSortFieldException,
    OwnerAlreadyHasTheOwnershipException,
    IncorrectEnumValueException,
    UserAlreadyHasCompanyException,
    IncorrectCompanyOrPropertyValueException,
    UserHasNoCompanyException,
    AddressAlreadyAssignedException,
    PropertyNotAvailableForRentException,
    UserCannotLeaseNotTheirPropertyException,
    ActiveLeaseException,
    IncorrectLeaseDatesException,
    CantModifyExpiredLeaseException,
    TenantAlreadyAcceptedRenewalException,
    TenantAlreadyDiscardedRenewalException,
    PropertyWithoutOwnerException,
    UserCannotRentTheirPropertyForThemselvesException,
    PaymentAlreadyAccepted
)
from src.core.tasks import scheduler

app = FastAPI(
    title="RealEstateAPI", description="Real Estate API", version="1.0"
)


root_router = APIRouter(prefix="/api")

root_router.include_router(user_router)
root_router.include_router(email_router)
root_router.include_router(jwt_router)
root_router.include_router(property_router)
root_router.include_router(company_router)
root_router.include_router(address_router)
root_router.include_router(lease_router)

app.include_router(root_router)


@app.exception_handler(AuthJWTException)
async def handle_auth_jwt_exception(
    request: Request, exception: AuthJWTException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exception.message}
    )


@app.exception_handler(DoesNotExist)
async def handle_does_not_exist(
    request: Request, exception: DoesNotExist
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exception)}
    )


@app.exception_handler(AlreadyExists)
async def handle_already_exists(
    request: Request, exception: AlreadyExists
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(IsOccupied)
async def handle_is_occupied(request: Request, exception: IsOccupied) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(ServiceException)
async def handle_service_exception(
    request: Request, exception: ServiceException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(AuthenticationException)
async def handle_authentication_exception(
    request: Request, exception: AuthenticationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exception)}
    )


@app.exception_handler(AuthorizationException)
async def handle_authorization_exception(
    request: Request, exception: AuthorizationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exception)}
    )


@app.exception_handler(AccountNotActivatedException)
async def handle_account_not_activated_exception(
    request: Request, exception: AccountNotActivatedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(AccountAlreadyDeactivatedException)
async def handle_account_already_deactivated_exception(
    request: Request, exception: AccountAlreadyDeactivatedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(AccountAlreadyActivatedException)
async def handle_account_already_activated_exception(
    request: Request, exception: AccountAlreadyActivatedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(UserCantDeactivateTheirAccountException)
async def handle_user_cant_deactivate_their_account_exception(
    request: Request, exception: UserCantDeactivateTheirAccountException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(UserCantActivateTheirAccountException)
async def handle_user_cant_activate_their_account_exception(
    request: Request, exception: UserCantActivateTheirAccountException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(NoSuchFieldException)
async def no_such_field_exception(
    request: Request, exception: NoSuchFieldException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(UnavailableFilterFieldException)
async def unavailable_filter_field_exception(
    request: Request, exception: UnavailableFilterFieldException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(UnavailableSortFieldException)
async def unavailable_sort_field_exception(
    request: Request, exception: UnavailableSortFieldException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(OwnerAlreadyHasTheOwnershipException)
async def owner_already_has_the_ownership_exception(
    request: Request, exception: OwnerAlreadyHasTheOwnershipException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(IncorrectEnumValueException)
async def incorrect_enum_value_exception(
    request: Request, exception: IncorrectEnumValueException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(UserAlreadyHasCompanyException)
async def user_already_has_company_exception(
    request: Request, exception: UserAlreadyHasCompanyException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(UserHasNoCompanyException)
async def user_has_no_company_exception(
    request: Request, exception: UserHasNoCompanyException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(IncorrectCompanyOrPropertyValueException)
async def incorrect_company_or_property_value_exception(
    request: Request, exception: IncorrectCompanyOrPropertyValueException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(AddressAlreadyAssignedException)
async def address_already_assigned_exception(
    request: Request, exception: AddressAlreadyAssignedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(PropertyNotAvailableForRentException)
async def property_not_available_for_rent_exception(
    request: Request, exception: PropertyNotAvailableForRentException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(UserCannotLeaseNotTheirPropertyException)
async def user_cannot_lease_not_their_property_exception(
    request: Request, exception: UserCannotLeaseNotTheirPropertyException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(ActiveLeaseException)
async def active_lease_exception(
    request: Request, exception: ActiveLeaseException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(IncorrectLeaseDatesException)
async def incorrect_lease_dates_exception(
    request: Request, exception: IncorrectLeaseDatesException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(CantModifyExpiredLeaseException)
async def cant_modify_expired_lease_exception(
    request: Request, exception: CantModifyExpiredLeaseException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(TenantAlreadyAcceptedRenewalException)
async def tenant_already_accepted_renewal_exception(
    request: Request, exception: TenantAlreadyAcceptedRenewalException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(TenantAlreadyDiscardedRenewalException)
async def tenant_already_discarded_renewal_exception(
    request: Request, exception: TenantAlreadyDiscardedRenewalException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(PropertyWithoutOwnerException)
async def property_without_owner_exception(
    request: Request, exception: PropertyWithoutOwnerException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(UserCannotRentTheirPropertyForThemselvesException)
async def user_cannot_rent_their_property_for_themselves_exception(
    request: Request, exception: UserCannotRentTheirPropertyForThemselvesException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(PaymentAlreadyAccepted)
def handle_payment_already_accepted_exception(
    request: Request, exception: PaymentAlreadyAccepted
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )