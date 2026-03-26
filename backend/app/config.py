"""Application configuration management"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Server
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    reload: bool = os.getenv("RELOAD", "true").lower() == "true"

    # Storage
    use_redis: bool = os.getenv("USE_REDIS", "false").lower() == "true"
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    auth_mock_fallback_enabled: bool = (
        os.getenv("AUTH_MOCK_FALLBACK_ENABLED", "false").lower() == "true"
    )

    # OpenCode
    opencode_base_url: str = os.getenv("OPENCODE_BASE_URL", "http://127.0.0.1:4096")
    opencode_username: str = os.getenv("OPENCODE_USERNAME", "opencode")
    opencode_password: str = os.getenv("OPENCODE_PASSWORD", "")

    # OpenWork
    openwork_base_url: str = os.getenv("OPENWORK_BASE_URL", "http://127.0.0.1:8787")
    openwork_token: str = os.getenv("OPENWORK_TOKEN", "")

    # Portal
    portal_name: str = os.getenv("PORTAL_NAME", "AI Portal")
    resources_path: str = os.getenv("RESOURCES_PATH", "config/resources.json")

    # CORS
    cors_origins: list = [
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量


# Global settings instance
settings = Settings()
