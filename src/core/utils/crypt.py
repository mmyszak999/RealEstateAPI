from passlib.context import CryptContext

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def hash_user_password(password: str) -> str:
    return passwd_context.hash(password)
