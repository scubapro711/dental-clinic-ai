"""
Configuration settings for DentalAI Backend.

This module uses pydantic-settings to load configuration from environment variables
or AWS Secrets Manager (in production).
"""

from typing import List, Literal, Optional
from pydantic import Field, field_validator
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
    APP_ENV: Literal["development", "staging", "production", "test"] = Field(default="development")
    
    @field_validator('APP_ENV', mode='before')
    @classmethod
    def normalize_app_env(cls, v: str) -> str:
        """Normalize APP_ENV values for backward compatibility."""
        if isinstance(v, str):
            v = v.strip().upper()
            # Map legacy values to standard ones
            if v == 'PROD':
                return 'production'
            return v.lower()
        return v
    
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    # AWS
    AWS_REGION: str = Field(default="us-east-1")
    USE_SECRETS_MANAGER: bool = Field(default=False)  # Enable in production

    # GCP (Google Cloud Platform)
    GCP_PROJECT_ID: str = Field(default="dentaflow-production")
    GCP_REGION: str = Field(default="us-central1")
    CLOUD_RUN_REVISION: str = Field(default="")  # Auto-populated in Cloud Run
    ENABLE_GCP_MONITORING: bool = Field(default=False)  # DISABLED: Causing deployment failures, needs fix

    # Security
    SECRET_KEY: str = Field(...)
    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Database (accepts PostgreSQL or SQLite for testing)
    DATABASE_URL: str = Field(...)
    
    # LangGraph Checkpointer Database (PostgreSQL for persistent memory)
    CHECKPOINT_DATABASE_URL: str = Field(
        default="postgresql://dentaflow:dentaflow123@localhost:5432/dentaflow_checkpoints"
    )

    # Redis (optional - falls back to in-memory cache)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Odoo (optional - only required if Odoo integration is enabled)
    ODOO_URL: Optional[str] = Field(default=None)
    ODOO_DB: Optional[str] = Field(default=None)
    ODOO_USERNAME: Optional[str] = Field(default=None)
    ODOO_PASSWORD: Optional[str] = Field(default=None)

    # LLM
    OPENAI_API_KEY: str = Field(...)
    ANTHROPIC_API_KEY: str = Field(default="")

    # Telegram Bot (optional - only required if Telegram integration is enabled)
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None)

    # Security Alerts Configuration
    SECURITY_ALERT_EMAIL_ENABLED: bool = Field(default=False)
    SECURITY_ALERT_EMAIL_TO: Optional[str] = Field(default=None)  # Comma-separated list
    SECURITY_ALERT_EMAIL_FROM: Optional[str] = Field(default="security@dentaflow.ai")
    SECURITY_ALERT_SMTP_HOST: Optional[str] = Field(default="smtp.gmail.com")
    SECURITY_ALERT_SMTP_PORT: int = Field(default=587)
    SECURITY_ALERT_SMTP_USERNAME: Optional[str] = Field(default=None)
    SECURITY_ALERT_SMTP_PASSWORD: Optional[str] = Field(default=None)
    
    SECURITY_ALERT_SLACK_ENABLED: bool = Field(default=False)
    SECURITY_ALERT_SLACK_WEBHOOK_URL: Optional[str] = Field(default=None)
    
    SECURITY_ALERT_TELEGRAM_ENABLED: bool = Field(default=False)
    SECURITY_ALERT_TELEGRAM_CHAT_ID: Optional[str] = Field(default=None)
    
    # Security Alert Thresholds
    SECURITY_ALERT_MIN_SEVERITY: str = Field(default="high")  # low, medium, high, critical

    # AWS Cognito
    COGNITO_USER_POOL_ID: str = Field(default="")
    COGNITO_CLIENT_ID: str = Field(default="")
    COGNITO_CLIENT_SECRET: str = Field(default="")
    COGNITO_REGION: str = Field(default="us-east-1")
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/api/v1/auth/google/callback")

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,https://dentaflow-frontend-688311017213.us-central1.run.app,https://dentaflow-frontend-staging-688311017213.us-central1.run.app,https://dentaflow-frontend-gmi5lyn5wq-uc.a.run.app,https://dentaflow-frontend-staging-gmi5lyn5wq-uc.a.run.app,https://dentaflow.ai,https://www.dentaflow.ai"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def security_alert_email_recipients(self) -> List[str]:
        """Parse SECURITY_ALERT_EMAIL_TO string into a list."""
        if not self.SECURITY_ALERT_EMAIL_TO:
            return []
        return [email.strip() for email in self.SECURITY_ALERT_EMAIL_TO.split(",")]

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
    def app_env(self) -> str:
        """Get normalized app environment."""
        return self.APP_ENV
    
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
