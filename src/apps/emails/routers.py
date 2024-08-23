from fastapi import BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.emails.schemas import EmailUpdateSchema
from src.apps.emails.services import change_email_service, confirm_email_change_service
from src.apps.user.models import User
from src.apps.user.services.user_services import activate_account_service
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

email_router = APIRouter(prefix="/email", tags=["emails"])


@email_router.post(
    "/confirm-account-activation/{token}",
    status_code=status.HTTP_200_OK,
)
def confirm_account_activation(
    token: str, db: Session = Depends(get_db), auth_jwt: AuthJWT = Depends()
) -> JSONResponse:
    activate_account_service(db, token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Account activated successfully!"},
    )
