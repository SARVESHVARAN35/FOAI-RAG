from functools import lru_cache
from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Enterprise IT Incident Knowledge RAG Assistant"
    APP_ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"

    JWT_SECRET_KEY: str = Field(min_length=32, repr=False)
    JWT_ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 10
    VECTOR_STORE_DIR: str = "vector_store"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
