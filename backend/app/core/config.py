"""
Configuration settings for DentalAI Backend.

This module uses pydantic-settings to load configuration from environment variables.
"""

from typing import List, Union
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    # Security
    SECRET_KEY: str = Field(...)
    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Database (allow SQLite for testing)
    DATABASE_URL: Union[PostgresDsn, str] = Field(...)
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str, info) -> str:
        """Allow SQLite URLs in test environment."""
        app_env = info.data.get("APP_ENV", "development")
        if app_env == "test" and v.startswith("sqlite://"):
            return v
        return v

    # Redis (allow mock for testing)
    REDIS_URL: Union[RedisDsn, str] = Field(...)

    # Neo4j
    NEO4J_URI: str = Field(...)
    NEO4J_USER: str = Field(...)
    NEO4J_PASSWORD: str = Field(...)

    # Odoo
    ODOO_URL: str = Field(...)
    ODOO_DB: str = Field(...)
    ODOO_USERNAME: str = Field(...)
    ODOO_PASSWORD: str = Field(...)

    # LLM
    OPENAI_API_KEY: str = Field(...)
    ANTHROPIC_API_KEY: str = Field(default="")

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = Field(...)

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Feature Flags
    ENABLE_MFA: bool = Field(default=False)
    ENABLE_FINE_TUNING: bool = Field(default=False)
    ENABLE_EXECUTIVE_AGENTS: bool = Field(default=False)
    ENABLE_SELF_HEALING: bool = Field(default=False)


# Global settings instance
settings = Settings()
