from fastapi import Depends, HTTPException, status

from src.apps.users.models import User
from src.dependencies.user import authenticate_user


def role_required(*allowed_roles: str, allow_owner: bool = False, owner_field: str = None):
    async def wrapper(
        user: User = Depends(authenticate_user),
        **kwargs
    ) -> User:
        user_role = user.role.name if user.role else None

        if user_role in allowed_roles:
            return user

        if allow_owner and owner_field and owner_field in kwargs:
            target_value = kwargs[owner_field]
            if getattr(user, owner_field) == target_value:
                return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return wrapper
