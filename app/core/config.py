from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    redis_url: str
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    embedding_model: str
    database_url: str


settings = Settings()