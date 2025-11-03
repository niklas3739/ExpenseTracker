import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "expense-tracker")
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
