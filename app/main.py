from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.config import create_directories
from app.database import create_db_and_tables
from app.api.main import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_directories()
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

app.include_router(api_router, prefix="/api")
