"""Central config — reads backend/.env. No secrets hardcoded."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "development"
    DATABASE_URL: str = ""
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 5
    DB_POOL_TIMEOUT: int = 30

    USE_MOCK_AI: bool = True
    AI_PROVIDER: str = "mock"  # mock | cloudflare | openrouter | groq | google | openai_compatible
    AI_PROVIDER_CHAIN: str = "cloudflare,openrouter,groq,google"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-3.8-flash"
    AI_BASE_URL: str = "https://api.groq.com/openai/v1"
    AI_TIMEOUT: int = 60
    AI_MAX_RETRIES: int = 2
    AI_CACHE_ENABLED: bool = True
    AI_CACHE_DIR: str = "./storage/ai_cache"
    CLOUDFLARE_ACCOUNT_ID: str = ""
    CLOUDFLARE_API_TOKEN: str = ""
    CLOUDFLARE_MODEL: str = "@cf/meta/llama-3.1-8b-instruct"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = ""
    # Legacy vendor keys (used if AI_API_KEY empty)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_TIMEOUT: int = 60
    GEMINI_MAX_RETRIES: int = 2
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 120
    ALLOW_DEV_SEED_OWNER: bool = True

    STORAGE_BACKEND: str = "local"
    STORAGE_DIR: str = "./storage"
    LOG_LEVEL: str = "INFO"


settings = Settings()
