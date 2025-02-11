from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.config import settings
from app.database import create_db_and_tables
from app.routers import user, group, venv, venv_package, repository, credential


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


@app.get("/info")
async def info():
    return {
        "settings": settings,
        "database_url": settings.database_url,
    }


app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(group.router, prefix="/group", tags=["group"])
app.include_router(venv.router, prefix="/venv", tags=["venv"])
app.include_router(venv_package.router, prefix="/venv_package", tags=["venv_package"])
app.include_router(repository.router, prefix="/repository", tags=["repository"])
app.include_router(credential.router, prefix="/credential", tags=["credential"])
