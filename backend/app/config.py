"""AgentFlow Configuration."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AgentFlow"
    app_version: str = "1.0.0"
    debug: bool = True

    # LLM
    llm_provider: str = "openai"
    llm_api_key: str = os.getenv("OPENAI_API_KEY", "sk-your-api-key")
    llm_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096

    # Database
    database_url: str = "sqlite+aiosqlite:///./agentflow.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Agent
    max_iterations: int = 10
    max_task_history: int = 50

    class Config:
        env_prefix = "AGENTFLOW_"
        env_file = ".env"


settings = Settings()
