from pydantic import BaseModel


class AccessTokenOutputSchema(BaseModel):
    access_token: str
    is_staff: str


class ConfirmationTokenSchema(BaseModel):
    token: str
