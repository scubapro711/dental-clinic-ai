from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True
    log_level: str = "info"
    title: str = "Dental Clinic AI Gateway"
    description: str = "The gateway for the Dental Clinic AI system."
    version: str = "0.1.0"

def get_settings():
    return Settings()

