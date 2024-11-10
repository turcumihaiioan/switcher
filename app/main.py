from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app import __version__
from app import models
from app.config import settings
from app.database import create_db_and_tables, SessionDep
from sqlmodel import select


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
def create_user(*, session: SessionDep, user: models.UserCreate):
    statement = select(models.User).where(models.User.username == user.username)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    db_user = models.User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get("/user", response_model=list[models.UserPublic])
def read_user(*, session: SessionDep):
    users = session.exec(select(models.User)).all()
    return users


@app.patch("/user/{user_id}", response_model=models.UserPublic)
def update_user(*, session: SessionDep, user_id: int, user: models.UserUpdate):
    db_user = session.get(models.User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
