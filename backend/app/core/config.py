"""
Configuration settings for DentalAI Backend.

This module uses pydantic-settings to load configuration from environment variables
or AWS Secrets Manager (in production).
"""

from typing import List, Literal
from pydantic import Field, RedisDsn
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
    APP_ENV: Literal["development", "staging", "production"] = Field(default="development")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    # AWS
    AWS_REGION: str = Field(default="us-east-1")
    USE_SECRETS_MANAGER: bool = Field(default=False)  # Enable in production

    # Security
    SECRET_KEY: str = Field(...)
    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Database (accepts PostgreSQL or SQLite for testing)
    DATABASE_URL: str = Field(...)

    # Redis
    REDIS_URL: RedisDsn = Field(...)

    # Neo4j (Optional - not currently used per CONTEXT_AND_GAPS_ANALYSIS.md)
    NEO4J_URI: str = Field(default="bolt://localhost:7687")
    NEO4J_USER: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(default="password")

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

    # AWS Cognito
    COGNITO_USER_POOL_ID: str = Field(default="")
    COGNITO_CLIENT_ID: str = Field(default="")
    COGNITO_CLIENT_SECRET: str = Field(default="")
    COGNITO_REGION: str = Field(default="us-east-1")

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Feature Flags
    FEATURE_PROACTIVE_SUGGESTIONS: bool = Field(default=True)
    FEATURE_WHATSAPP: bool = Field(default=False)
    FEATURE_ANALYTICS: bool = Field(default=True)
    FEATURE_MFA: bool = Field(default=False)
    FEATURE_FINE_TUNING: bool = Field(default=False)
    FEATURE_EXECUTIVE_AGENTS: bool = Field(default=False)
    FEATURE_SELF_HEALING: bool = Field(default=False)

    # Environment helpers
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.APP_ENV == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.APP_ENV == "development"
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging."""
        return self.APP_ENV == "staging"

    def get_database_url(self) -> str:
        """
        Get database URL from Secrets Manager or environment.
        
        Returns:
            Database connection string
        """
        if self.USE_SECRETS_MANAGER:
            try:
                from app.core.secrets import secrets_manager
                creds = secrets_manager.get_database_credentials()
                return f"postgresql://{creds['username']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"
            except Exception as e:
                print(f"Warning: Failed to get database credentials from Secrets Manager: {e}")
                print("Falling back to DATABASE_URL from environment")
        
        return self.DATABASE_URL
    
    def get_openai_key(self) -> str:
        """
        Get OpenAI API key from Secrets Manager or environment.
        
        Returns:
            OpenAI API key
        """
        if self.USE_SECRETS_MANAGER:
            try:
                from app.core.secrets import secrets_manager
                return secrets_manager.get_openai_key()
            except Exception as e:
                print(f"Warning: Failed to get OpenAI key from Secrets Manager: {e}")
                print("Falling back to OPENAI_API_KEY from environment")
        
        return self.OPENAI_API_KEY
    
    def get_telegram_token(self) -> str:
        """
        Get Telegram bot token from Secrets Manager or environment.
        
        Returns:
            Telegram bot token
        """
        if self.USE_SECRETS_MANAGER:
            try:
                from app.core.secrets import secrets_manager
                return secrets_manager.get_telegram_token()
            except Exception as e:
                print(f"Warning: Failed to get Telegram token from Secrets Manager: {e}")
                print("Falling back to TELEGRAM_BOT_TOKEN from environment")
        
        return self.TELEGRAM_BOT_TOKEN
    
    def get_odoo_credentials(self) -> dict:
        """
        Get Odoo credentials from Secrets Manager or environment.
        
        Returns:
            Dictionary with url, db, username, password
        """
        if self.USE_SECRETS_MANAGER:
            try:
                from app.core.secrets import secrets_manager
                return secrets_manager.get_odoo_credentials()
            except Exception as e:
                print(f"Warning: Failed to get Odoo credentials from Secrets Manager: {e}")
                print("Falling back to ODOO_* from environment")
        
        return {
            'url': self.ODOO_URL,
            'db': self.ODOO_DB,
            'username': self.ODOO_USERNAME,
            'password': self.ODOO_PASSWORD,
        }


# Global settings instance
settings = Settings()
