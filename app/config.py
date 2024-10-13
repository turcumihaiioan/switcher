from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
        )
    database_type: str | None = None
    database_file: str | None = None
    database_host: str | None = None
    database_port: int | None = None
    database_db: str | None = None
    database_user: str | None = None
    database_password: str | None = None

    @property
    def database_url(self) -> str:
        if self.database_type == "sqlite":
            return f"sqlite:///{self.database_file}"
        else:
            raise ValueError(f"Unsupported DATABASE_TYPE: {self.database_type}")

settings = Settings()
