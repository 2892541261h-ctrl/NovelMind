from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "NovelMind"
    app_version: str = "0.1.0"
    environment: str = "local"
    ai_provider: str = "mock"
    database_url: str = "sqlite:///./novelmind.sqlite3"


settings = Settings()
