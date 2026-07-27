import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "JackeyFootball API"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./jackeyfootball.db"
    FOOTBALL_DATA_API_KEY: str = ""
    FOOTBALL_DATA_BASE_URL: str = "https://api.football-data.org/v4"

    # TheSportsDB 免费数据源（无需注册即可用默认测试 Key "3"）
    # 个人 Key 通过 .env 的 THESPORTSDB_API_KEY 覆盖（Patreon 订阅后获取）
    THESPORTSDB_API_KEY: str = "3"

    class Config:
        env_file = ".env"


settings = Settings()
