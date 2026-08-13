from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Typed fields (not raw os.getenv strings) mean a bad .env value, e.g.
    # TOP_K="not-a-number", fails fast at startup with a clear ValidationError
    # instead of crashing later inside a retrieval call.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Groq (LLM) ---
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model_primary: str = Field(default="openai/gpt-oss-120b", alias="GROQ_MODEL_PRIMARY")
    groq_model_fallback: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL_FALLBACK")
    groq_guard_model: str = Field(default="meta-llama/llama-prompt-guard-2-86m", alias="GROQ_GUARD_MODEL")
    groq_max_concurrency: int = Field(default=2, alias="GROQ_MAX_CONCURRENCY")

    # --- Qdrant (vector DB) ---
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str = Field(default="", alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="pkc_tech", alias="QDRANT_COLLECTION")

    # --- Embeddings & retrieval ---
    embed_model: str = Field(default="BAAI/bge-small-en-v1.5", alias="EMBED_MODEL")
    embed_dim: int = Field(default=384, alias="EMBED_DIM")
    top_k: int = Field(default=8, alias="TOP_K")
    use_hybrid: bool = Field(default=True, alias="USE_HYBRID")
    rrf_k: int = Field(default=60, alias="RRF_K")

    # --- Guardrail thresholds (SPEC §4.4) ---
    injection_threshold: float = Field(default=0.8, alias="INJECTION_THRESHOLD")
    out_of_scope_threshold: float = Field(default=0.25, alias="OUT_OF_SCOPE_THRESHOLD")
    faithfulness_threshold: float = Field(default=0.7, alias="FAITHFULNESS_THRESHOLD")
    enable_groundedness_check: bool = Field(default=True, alias="ENABLE_GROUNDEDNESS_CHECK")
    guardrails_fail_closed: bool = Field(default=True, alias="GUARDRAILS_FAIL_CLOSED")

    # --- Auth (JWT) ---
    jwt_secret: str = Field(default="dev-only-change-me", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60, alias="JWT_EXPIRE_MINUTES")

    # --- LangSmith / LangChain tracing ---
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: str = Field(default="", alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="pkc-secure-knowledge", alias="LANGCHAIN_PROJECT")
    langchain_endpoint: str = Field(default="https://api.smith.langchain.com", alias="LANGCHAIN_ENDPOINT")

    # --- Observability / budget ---
    ledger_db_path: str = Field(default="data/ledger.db", alias="LEDGER_DB_PATH")
    daily_token_budget: int = Field(default=50000, alias="DAILY_TOKEN_BUDGET")
    daily_shadow_cost_alert_usd: float = Field(default=5.0, alias="DAILY_SHADOW_COST_ALERT_USD")

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()