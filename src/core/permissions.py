from fastapi import Depends, HTTPException, status
from functools import wraps

from src.apps.users.models import User
from src.dependencies.user import authenticate_user


def role_required(*allowed_roles: str, allow_owner: bool = False, owner_field: str = None):
    def decorator(endpoint):
        @wraps(endpoint)
        async def wrapper(
            *args,
            user: User = Depends(authenticate_user),
            **kwargs
        ):
            user_role = user.role.name if user.role else None

            # roles check
            if user_role in allowed_roles:
                return await endpoint(*args, **kwargs)

            # owner check
            if allow_owner and owner_field and owner_field in kwargs:
                if getattr(user, owner_field) == kwargs[owner_field]:
                    return await endpoint(*args, **kwargs)

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

        return wrapper
    return decorator
