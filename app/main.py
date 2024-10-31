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

@app.post("/user")
def create_user(user: models.User, session: Session = Depends(get_session)) -> models.User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
