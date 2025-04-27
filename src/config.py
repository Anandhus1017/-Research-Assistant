from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Research Assistant"
    VERSION: str = "1.0.0"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    VECTOR_DB_PATH: str = "vector_db"
    MAX_PAPERS: int = 10
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()