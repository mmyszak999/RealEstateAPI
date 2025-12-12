from fastapi import HTTPException, status
from functools import wraps
from src.apps.users.models import User


def role_required(*allowed_roles: str, allow_owner: bool = False, owner_field: str = None):
    def decorator(endpoint):
        @wraps(endpoint)
        async def wrapper(
            *args,
            user: User,
            **kwargs
        ):
            user_role = user.role.name if user.role else None

            if user_role in allowed_roles:
                return await endpoint(*args, user=user, **kwargs)

            if allow_owner and owner_field and owner_field in kwargs:
                if getattr(user, owner_field, None) == kwargs[owner_field]:
                    return await endpoint(*args, user=user, **kwargs)

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

        return wrapper
    return decorator
