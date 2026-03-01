from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://trends:trends@localhost:5432/trends"
    SYNC_DATABASE_URL: str = "postgresql://trends:trends@localhost:5432/trends"
    
    # LLM Settings (for summarizing/tagging)
    LLM_PROVIDER: str = "openai" # default to openai
    LLM_API_KEY: Optional[str] = None
    
    # Event Integration
    CONNPASS_API_KEY: Optional[str] = None
    
    # Other configs
    APP_NAME: str = "Search Trend Scout API"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
