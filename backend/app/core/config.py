"""Central config — reads backend/.env. No secrets hardcoded."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "development"
    DATABASE_URL: str = ""
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 5
    DB_POOL_TIMEOUT: int = 30

    AI_PROVIDER: str = "google"  # google | openai_compatible (groq, openrouter, ollama via base_url)
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-3.8-flash"
    AI_BASE_URL: str = "https://api.groq.com/openai/v1"
    AI_TIMEOUT: int = 60
    AI_MAX_RETRIES: int = 2
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

    STORAGE_BACKEND: str = "local"
    STORAGE_DIR: str = "./storage"
    LOG_LEVEL: str = "INFO"


settings = Settings()
