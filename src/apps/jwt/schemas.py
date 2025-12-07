from pydantic import BaseModel


class AccessTokenOutputSchema(BaseModel):
    access_token: str
    user_role: str


class ConfirmationTokenSchema(BaseModel):
    token: str
