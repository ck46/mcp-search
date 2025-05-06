from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()  # singleton import 