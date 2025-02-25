import datetime
import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseSettings

PLAN_CART_API_ROOT_PATH: str = "/plan_cart"


# 部署狀態管理
class DeployStatus(str, Enum):
    Local = "local"  # 本地/本機 環境
    Development = "development"  # 開發環境
    Production = "production"  # 正式環境
    Test = "test"  # 測試 環境/模式

class GenerallySettings(BaseSettings):
    ACCESS_CONTROL_ALLOW_ORIGIN: Optional[list] = ["*"]
    environment: str
    IS_DEBUG: bool


class LocalSettings(GenerallySettings):
    environment: str = DeployStatus.Local

    IS_DEBUG: bool = True
    FASTAPI_DOCS_URL: Optional[str] = "{}/docs"
    FASTAPI_OPENAPI_URL: Optional[str] = "{}/{}/openapi.json"
    FASTAPI_REDOC_URL: Optional[str] = "{}/redoc"

    DB_DATABASE: str = "sqlite3.db" 
    HOME_URL: str = "/Web_Project"

    class Config:
        env_file = "./local.env"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

@lru_cache
def get_settings() -> GenerallySettings:
    deploy_status = os.getenv("environment", default=DeployStatus.Local)

    if deploy_status in {DeployStatus.Local}:
        runtime_settings = LocalSettings()
        
    return runtime_settings