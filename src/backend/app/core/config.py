from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/predprof"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    ml_service_url: str = "http://ml:8000"

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    log_level: str = "INFO"

    admin_username: str = "admin"
    admin_password: str = "admin123"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @property
    def database_url_sync(self) -> str:
        return self.database_url.replace("+asyncpg", "+psycopg2")


settings = Settings()
