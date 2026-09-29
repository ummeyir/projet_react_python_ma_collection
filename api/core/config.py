from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = "mot_de passe_très_secret"
    algorithm: str = "123"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+asyncpg://collection:collection@localhost:5432/collection"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()