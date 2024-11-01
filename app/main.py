from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from app import __version__
from app import models
from app.config import settings
from app.database import create_db_and_tables, get_session
from sqlmodel import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="switcher",
    version=__version__,
    license_info={
        "name": "GNU General Public License v3.0 or later",
        "identifier": "GPL-3.0-or-later",
    },
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/info")
async def info():
    return {
        "settings": settings,
        "database_url": settings.database_url,
    }

@app.post("/user", response_model=models.UserPublic)
def create_user(*, session: Session = Depends(get_session), user: models.UserCreate):
    db_user = models.User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
