"""應用程式配置"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """應用程式設定"""

    # API 設定
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "CFD 求解器 API"
    VERSION: str = "1.0.0"

    # CORS 設定
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # 求解器設定
    MAX_GRID_SIZE: int = 200
    MIN_GRID_SIZE: int = 10
    DEFAULT_GRID_SIZE: int = 41

    class Config:
        case_sensitive = True


settings = Settings()
