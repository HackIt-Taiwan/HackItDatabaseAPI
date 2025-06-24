from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Optional, Annotated
import secrets
import logging

logger = logging.getLogger(__name__)

class DatabaseSettings(BaseSettings):
    """Database service configuration settings with validation."""
    
    # Database connection
    MONGODB_URI: str = Field(..., description="MongoDB connection URI")
    MONGODB_DATABASE: str = Field(..., description="MongoDB database name")
    MONGODB_MAX_POOL_SIZE: int = Field(default=10, description="MongoDB connection pool size")
    MONGODB_MIN_POOL_SIZE: int = Field(default=1, description="MongoDB minimum pool size")
    MONGODB_CONNECT_TIMEOUT: int = Field(default=10000, description="MongoDB connection timeout (ms)")
    
    # API Security
    API_SECRET_KEY: str = Field(..., description="HMAC secret key for API authentication")
    API_KEY_ROTATION_ENABLED: bool = Field(default=False, description="Enable API key rotation")
    API_RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable API rate limiting")
    API_RATE_LIMIT_REQUESTS: int = Field(default=100, description="Requests per minute limit")
    
    # Request timeout and signature validation
    REQUEST_TIMEOUT_SECONDS: int = Field(default=30, description="Request timeout in seconds")
    SIGNATURE_VALIDITY_WINDOW: int = Field(default=300, description="HMAC signature validity window in seconds")
    
    # CORS and domain security
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000,https://hackit.tw,https://*.hackit.tw",
        description="Allowed CORS origins (comma-separated)"
    )
    
    ALLOWED_HOSTS: str = Field(
        default="localhost,127.0.0.1,hackit.tw,*.hackit.tw",
        description="Allowed hosts for domain validation (comma-separated)"
    )
    
    # Service configuration
    SERVICE_HOST: str = Field(default="0.0.0.0", description="Service host")
    SERVICE_PORT: int = Field(default=8001, ge=1, le=65535, description="Service port")
    SERVICE_NAME: str = Field(default="hackit-database-service", description="Service name")
    SERVICE_VERSION: str = Field(default="1.1.0", description="Service version")
    
    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="JSON", description="Log format (JSON or TEXT)")
    LOG_FILE_ENABLED: bool = Field(default=False, description="Enable file logging")
    LOG_FILE_PATH: str = Field(default="logs/database-service.log", description="Log file path")
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment (development, staging, production)")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Feature flags
    FEATURES_AUTO_MIGRATION: bool = Field(default=True, description="Enable automatic database migrations")
    FEATURES_SCHEMA_VALIDATION: bool = Field(default=True, description="Enable strict schema validation")
    FEATURES_AUDIT_LOGGING: bool = Field(default=False, description="Enable audit logging")
    
    # Performance settings
    CACHE_ENABLED: bool = Field(default=False, description="Enable caching")
    CACHE_TTL_SECONDS: int = Field(default=300, description="Cache TTL in seconds")
    MAX_CONNECTIONS: int = Field(default=100, description="Maximum concurrent connections")
    
    @field_validator('API_SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v):
        """Validate API secret key strength."""
        if len(v) < 32:
            logger.warning("API secret key is shorter than recommended 32 characters")
        return v
    
    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed_envs = ['development', 'staging', 'production']
        if v.lower() not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v.lower()
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()
    
    @field_validator('LOG_FORMAT')
    @classmethod
    def validate_log_format(cls, v):
        """Validate log format."""
        allowed_formats = ['JSON', 'TEXT']
        if v.upper() not in allowed_formats:
            raise ValueError(f"Log format must be one of {allowed_formats}")
        return v.upper()
    
    def get_allowed_origins_list(self) -> List[str]:
        """Get ALLOWED_ORIGINS as a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',') if origin.strip()]
    
    def get_allowed_hosts_list(self) -> List[str]:
        """Get ALLOWED_HOSTS as a list."""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(',') if host.strip()]
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == 'development'
    
    def generate_new_secret_key(self) -> str:
        """Generate a new secure secret key."""
        return secrets.token_urlsafe(32)
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Global settings instance
settings = DatabaseSettings()

# Validate critical settings on import
if settings.is_production():
    logger.info("Running in production mode - all security features enabled")
    if settings.DEBUG:
        logger.warning("Debug mode is enabled in production - this is not recommended")
else:
    logger.info(f"Running in {settings.ENVIRONMENT} mode") 