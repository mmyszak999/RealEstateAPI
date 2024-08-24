from fastapi import BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.apps.users.services.activation_services import activate_account_service
from src.dependencies.get_db import get_db

email_router = APIRouter(prefix="/email", tags=["emails"])


@email_router.post(
    "/confirm-account-activation/{token}",
    status_code=status.HTTP_200_OK,
)
async def confirm_account_activation(
    token: str, db: AsyncSession = Depends(get_db), auth_jwt: AuthJWT = Depends()
) -> JSONResponse:
    await activate_account_service(db, token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Account activated successfully!"},
    )
