from typing import Union

from fastapi import BackgroundTasks, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.users.models import User
from src.apps.users.schemas import (
    UserInfoOutputSchema,
    UserLoginInputSchema,
    UserOutputSchema,
    UserUpdateSchema,
    UserRegisterSchema
)
from src.apps.users.services.activation_services import (
    activate_single_user,
    deactivate_single_user,
)
from src.apps.users.services.user_services import (
    create_single_user,
    get_access_token_schema,
    get_all_users,
    get_single_user,
    update_single_user,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post(
    "/create", response_model=UserInfoOutputSchema, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_input: UserRegisterSchema,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
) -> UserInfoOutputSchema:
    return await create_single_user(session, user_input, background_tasks)


@user_router.post(
    "/create-with-email-activation",
    response_model=UserInfoOutputSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_input: UserRegisterSchema,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
) -> UserInfoOutputSchema:
    return await create_single_user(
        session, user_input, background_tasks, with_email_activation=True
        )


@user_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=AccessTokenOutputSchema
)
async def login_user(
    user_login_schema: UserLoginInputSchema,
    auth_jwt: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_db),
) -> AccessTokenOutputSchema:
    return await get_access_token_schema(user_login_schema, session, auth_jwt)


@user_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user)],
    response_model=UserOutputSchema,
)
async def get_logged_user(
    request_user: User = Depends(authenticate_user),
) -> UserOutputSchema:
    return UserOutputSchema.from_orm(request_user)


@user_router.get(
    "/",
    response_model=PagedResponseSchema[UserInfoOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[UserInfoOutputSchema]:
    await check_if_staff(request_user)
    return await get_all_users(
        session, page_params, 
        output_schema=UserInfoOutputSchema,
        query_params=request.query_params.multi_items()
    )


@user_router.get(
    "/all",
    response_model=PagedResponseSchema[UserOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_every_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[UserOutputSchema]:
    await check_if_staff(request_user)
    return await get_all_users(
        session,
        page_params,
        only_active=False,
        query_params=request.query_params.multi_items(),
    )


@user_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> UserOutputSchema:
    await check_if_staff(request_user)
    return await get_single_user(session, user_id)


@user_router.patch(
    "/{user_id}",
    response_model=UserInfoOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: str,
    user_input: UserUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> UserInfoOutputSchema:
    if (await check_if_staff_or_owner(request_user, "id", user_id)):
        return await update_single_user(session, user_input, user_id)


@user_router.patch(
    "/{user_id}/deactivate",
    status_code=status.HTTP_200_OK,
)
async def deactivate_user(
    user_id: str,
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    await check_if_staff(request_user)
    await deactivate_single_user(session, user_id, request_user.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "The account has been deactivated!"},
    )

@user_router.patch(
    "/{user_id}/activate",
    status_code=status.HTTP_200_OK,
)
async def activate_user(
    user_id: str,
    request_user: User = Depends(authenticate_user),
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    await check_if_staff(request_user)
    await activate_single_user(session, user_id, request_user.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "The account has been activated!"},
    )
