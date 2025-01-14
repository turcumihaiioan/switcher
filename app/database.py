from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine, text

from app.config import settings

connect_args = {"check_same_thread": False}
engine = create_engine(settings.database_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    if settings.database_type == "sqlite":
        with engine.connect() as connection:
            connection.execute(text("PRAGMA foreign_keys=ON"))


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
