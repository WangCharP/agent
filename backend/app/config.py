import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """
    应用配置类
    会自动读取环境变量或 .env 文件
    """
    
    # --- 基础配置 ---
    APP_NAME: str = "Backend"
    APP_ENV: Literal["development", "production", "testing"] = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # --- 路径配置 ---
    # 自动拼接路径，避免手动写 os.path.join
    BASE_DIR: Path = BASE_DIR
    # 假设 frontend 与 backend 同级
    STATIC_DIR: Path = BASE_DIR.parent / "frontend" / "public"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"

    # --- LLM (大模型) 配置 ---
    OPENAI_API_KEY: str | None = None # 选填，如果没有则使用模拟模式
    OPENAI_BASE_URL: str | None = None
    SMART_LLM_MODEL: str = "gpt-4o"
    FAST_LLM_MODEL: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.55
    
    # 其他厂商 Key
    KIMI_BASE_URL : str |None = None
    KIMI_API_KEY: str | None = None
    DEEPSEEK_BASE_URL: str | None = None
    DEEPSEEK_API_KEY: str | None = None

    # --- 搜索工具配置 ---
    TAVILY_API_KEY: str | None = None  # 选填，允许为 None
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."

    # --- Pydantic 配置 ---
    # 告诉 Pydantic 去哪里找 .env 文件
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True, # 区分大小写 (通常环境变量大写)
        extra="ignore"       # 忽略 .env 中多余的字段，不报错
    )

    def create_dirs(self):
        """辅助方法：确保必要的目录存在"""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def model_post_init(self, __context):
        """
        Pydantic v2 钩子：在模型初始化后执行
        用于处理 API Key 的自动映射
        """
        # 如果没有设置 OPENAI_API_KEY，尝试使用其他厂商的 Key
        if self.DEEPSEEK_API_KEY and self.DEEPSEEK_BASE_URL:
            print("Using DeepSeek API Key")
            self.OPENAI_API_KEY = self.DEEPSEEK_API_KEY
            self.OPENAI_BASE_URL = self.DEEPSEEK_BASE_URL
            self.SMART_LLM_MODEL = "deepseek-chat"
        elif self.KIMI_API_KEY and self.DEEPSEEK_BASE_URL:
            print("Using Kimi (Moonshot) API Key")
            self.OPENAI_API_KEY = self.KIMI_API_KEY
            self.OPENAI_BASE_URL = "https://api.moonshot.cn/v1"
            self.SMART_LLM_MODEL = "moonshot-v1-8k"

# 实例化配置对象，单例模式
settings = Settings()

# 可以在启动时自动创建目录
settings.create_dirs()