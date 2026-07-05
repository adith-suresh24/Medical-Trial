import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Hospital Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "default-secret-key-change-in-production"

    DATABASE_URL: str = "sqlite:///./hospital.db"

    JWT_SECRET_KEY: str = "default-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    AI_API_URL: str = ""
    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-3.5-turbo"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    PDF_OUTPUT_DIR: str = "./generated_pdfs"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
