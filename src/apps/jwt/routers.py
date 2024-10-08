from fastapi import APIRouter, Depends, Response, status

from src.apps.users.models import User
from src.dependencies.user import authenticate_user

jwt_router = APIRouter(prefix="/token", tags=["tokens"])


@jwt_router.post("/verify/", status_code=status.HTTP_204_NO_CONTENT)
async def verify_token(request_user: User = Depends(authenticate_user)) -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
