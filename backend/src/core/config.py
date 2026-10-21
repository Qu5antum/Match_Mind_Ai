from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_NAME: str = "match_mind_db"

    APP_NAME: str = "Match_mind_AI"
    debug: bool = True
    cors_origins: list[str] = ["*"]

    GEMINI_MODEL: str | None = None
    GEMINI_API_KEY: str | None = None
    GEMINI_TIMEOUT_MS: int = 30_000

    MANUS_MODEL: str | None = None
    MANUS_API_KEY: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def URL_DATABASE(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Config()