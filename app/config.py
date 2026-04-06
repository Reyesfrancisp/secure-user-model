from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/fastapi_db"
    
    class Config:
        env_file = ".env"

settings = Settings()