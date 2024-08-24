from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    MYSQL_DB: str
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_ROOT_USER: str
    MYSQL_ROOT_PASSWORD: str
    MYSQL_PASSWORD: str
    MYSQL_PORT: int
    TEST_MYSQL_DB: str
    ASYNC: bool = True
    TESTING: bool = False
    USE_ROOT: bool = True

    class Config:
        env_file = ".env"

    @property
    def mysql_url(self) -> str:
        db_name = self.TEST_MYSQL_DB if self.TESTING else self.MYSQL_DB
        db_driver = "mysql+asyncmy" if self.ASYNC else "mysql+pymysql"

        if self.USE_ROOT:
            user, password = self.MYSQL_ROOT_USER, self.MYSQL_ROOT_PASSWORD
        else:
            user, password = self.MYSQL_USER, self.MYSQL_PASSWORD

        return (
            f"{db_driver}://{user}:{password}@"
            f"{self.MYSQL_HOST}:{self.MYSQL_PORT}/{db_name}"
        )


settings = DatabaseSettings()
