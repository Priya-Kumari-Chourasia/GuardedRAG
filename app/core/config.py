from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model_primary: str = Field(default="openai/gpt-oss-120b", alias="GROQ_MODEL_PRIMARY")
    groq_model_fallback: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL_FALLBACK")
    groq_max_concurrency: int = Field(default=2, alias="GROQ_MAX_CONCURRENCY")

    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str = Field(default="", alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="pkc_docs", alias="QDRANT_COLLECTION")

    jwt_secret: str = Field(default="dev-only-change-me", alias="JWT_SECRET")

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()