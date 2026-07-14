import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Agente RAG Entregable 5")
    app_env: str = os.getenv("APP_ENV", "local")
    azure_sql_connection_string: str = os.getenv("AZURE_SQL_CONNECTION_STRING", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
    top_k: int = int(os.getenv("TOP_K", "3"))
    llm_provider: str = os.getenv("LLM_PROVIDER", "demo").lower()


settings = Settings()
