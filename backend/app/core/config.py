"""Application settings via Pydantic BaseSettings."""
import os
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # PostgreSQL Connection String / URI (takes precedence if provided)
    DATABASE_URL:      str = ""

    # Individual PostgreSQL Settings (fallback)
    POSTGRES_HOST:     str = "localhost"
    POSTGRES_PORT:     int = 5432
    POSTGRES_DB:       str = "commercepulse"
    POSTGRES_USER:     str = "commercepulse"
    POSTGRES_PASSWORD: str = "changeme"

    # Application
    APP_ENV:  str = "development"
    API_KEY: str = Field(..., env="API_KEY")
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:4000", "http://127.0.0.1:4000", "http://127.0.0.1:3000"]

    # Redis (Celery broker/result backend)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Embedding model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMS:  int = 384

    # AI Agents API (local default 8002 — 8001 is often taken by other apps)
    # Restart the API after changing AI_AGENTS_URL in .env.
    AI_AGENTS_URL: str = "http://127.0.0.1:8002"

    # Groq API Key
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    GROQ_API_KEY_2: str = ""
    GROQ_API_KEY_3: str = ""
    FALLBACK_GROQ_API_KEY: str = ""
    GROQ_CHAT_MODEL: str = "llama-3.1-8b-instant"
    GROQ_FALLBACK_MODEL: str = "openai/gpt-oss-20b"

    @property
    def _pw(self) -> str:
        """URL-encode the password so special chars (@ % : /) don't break the DSN."""
        return quote_plus(self.POSTGRES_PASSWORD)

    @property
    def async_db_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            
            # Ensure SSL is appended for remote databases like Supabase
            if "supabase.co" in url or "supabase.com" in url:
                if "?" in url:
                    if "ssl" not in url:
                        url += "&ssl=require"
                else:
                    url += "?ssl=require"
            return url

        base = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self._pw}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        if "supabase.co" in self.POSTGRES_HOST:
            base += "?ssl=require"
        return base

    @property
    def sync_db_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
                
            if "supabase.co" in url or "supabase.com" in url:
                if "?" in url:
                    if "sslmode" not in url:
                        url += "&sslmode=require"
                else:
                    url += "?sslmode=require"
            return url

        base = (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self._pw}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        if "supabase.co" in self.POSTGRES_HOST:
            base += "?sslmode=require"
        return base


settings = Settings()

# LangChain / Groq clients read os.environ, not Pydantic. Mirror keys so chat tools work.
for _name, _val in (
    ("GROQ_API_KEY", settings.GROQ_API_KEY),
    ("GROQ_API_KEY_2", settings.GROQ_API_KEY_2),
    ("GROQ_API_KEY_3", settings.GROQ_API_KEY_3),
    ("FALLBACK_GROQ_API_KEY", settings.FALLBACK_GROQ_API_KEY),
    ("AI_AGENTS_URL", settings.AI_AGENTS_URL),
):
    if _val:
        os.environ.setdefault(_name, _val)

