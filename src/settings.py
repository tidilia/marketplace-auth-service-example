from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # postgres_host: str
    # postgres_database_name: str
    # postgres_password: str
    # postgres_port: int
    # postgres_username: str

    database_url: str = Field(validation_alias="DATABASE_URL")

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    jwt_refresh_expire_days: int = 30

    # @property
    # def database_url(self) -> str:
    #     return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"
