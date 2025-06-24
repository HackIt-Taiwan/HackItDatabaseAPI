from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    # Database connection
    MONGODB_URI: str
    MONGODB_DATABASE: str
    
    # API Security
    API_SECRET_KEY: str
    ALLOWED_ORIGINS: list = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://hackit.tw",
        "https://*.hackit.tw"
    ]
    
    # Service configuration
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8001
    
    class Config:
        env_file = ".env"

settings = DatabaseSettings() 