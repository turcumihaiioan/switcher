from fastapi import APIRouter

from app.config import settings

from app.api.routers import (
    user,
    group,
    repository,
    credential,
    inventory,
    venv,
    venv_package,
)

router = APIRouter()


@router.get("/info")
async def info():
    return {
        "settings": settings,
        "database_url": settings.database_url,
    }


router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(group.router, prefix="/group", tags=["group"])
router.include_router(repository.router, prefix="/repository", tags=["repository"])
router.include_router(credential.router, prefix="/credential", tags=["credential"])
router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
router.include_router(venv.router, prefix="/venv", tags=["venv"])
router.include_router(
    venv_package.router, prefix="/venv_package", tags=["venv_package"]
)
