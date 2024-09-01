from pydantic import BaseSettings


class GeneralSettings(BaseSettings):
    SECRET_KEY: str
    authjwt_secret_key: str
    SECURITY_PASSWORD_SALT: str
    SEND_EMAILS: bool

    class Config:
        env_file = ".env"


settings = GeneralSettings()
