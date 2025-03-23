import os
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    database_type: str | None = None
    database_file: str | None = None
    database_host: str | None = None
    database_port: int | None = None
    database_db: str | None = None
    database_user: str | None = None
    database_password: str | None = None

    data_dir: str = "data"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def venv_dir(self) -> str:
        return f"{self.data_dir}/venv"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def repository_dir(self) -> str:
        return f"{self.data_dir}/repository"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def db_dir(self) -> str | None:
        if self.database_type == "sqlite":
            return f"{self.data_dir}/db"
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        if self.database_type == "sqlite":
            return f"sqlite:///{self.db_dir}/{self.database_file}"
        raise ValueError(f"Unsupported DATABASE_TYPE: {self.database_type}")


settings = Settings()


def create_directories():
    BASE_DIR = Path(__file__).parent.parent

    DATA_DIR = Path(BASE_DIR) / settings.data_dir
    os.makedirs(DATA_DIR, exist_ok=True)

    REPOSITORY_DIR = Path(BASE_DIR) / settings.repository_dir
    os.makedirs(REPOSITORY_DIR, exist_ok=True)

    VENV_DIR = Path(BASE_DIR) / settings.venv_dir
    os.makedirs(VENV_DIR, exist_ok=True)
    if settings.db_dir is not None:
        DB_DIR = Path(BASE_DIR) / settings.db_dir
        os.makedirs(DB_DIR, exist_ok=True)
