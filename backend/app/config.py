import os
from pathlib import Path
from typing import Literal, Dict, Any
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """应用配置类"""
    
    # 强制指定 .env 的绝对路径，防止读取失败
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    APP_NAME: str = "Backend"
    APP_ENV: Literal["development", "production", "testing"] = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    BASE_DIR: Path = BASE_DIR
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    TEMPERATURE: float = 0.55
    
    # 定义 Key 字段，Pydantic 会自动从 .env 填充
    KIMI_BASE_URL : str | None = None
    KIMI_API_KEY: str | None = None
    DEEPSEEK_BASE_URL: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    QWEN_BASE_URL: str | None = None
    QWEN_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None 

    def create_dirs(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 动态生成 Solver 配置
    @computed_field
    @property
    def SOLVER_MODEL(self) -> Dict[str, Any]:
        return {
            "name": "deepseek-chat",
            "config": {
                "base_url": self.DEEPSEEK_BASE_URL,
                "api_key": self.DEEPSEEK_API_KEY,
            }
        }

    # 动态生成并行搜索模型列表
    @computed_field
    @property
    def SEARCH_MODELS(self) -> Dict[str, Any]:
        models = {}
        if self.DEEPSEEK_API_KEY:
            models["deepseek-reasoner"] = {
                "base_url": self.DEEPSEEK_BASE_URL,
                "api_key": self.DEEPSEEK_API_KEY,
            }
        if self.KIMI_API_KEY:
            models["moonshot-v1-8k"] = {
                "base_url": self.KIMI_BASE_URL,
                "api_key": self.KIMI_API_KEY,
            }
        if self.QWEN_API_KEY:
            models["qwen-plus"] = {
                "base_url": self.QWEN_BASE_URL,
                "api_key": self.QWEN_API_KEY,
            }
        return models

settings = Settings()
settings.create_dirs()