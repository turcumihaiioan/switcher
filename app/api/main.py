from fastapi import APIRouter

from app.config import settings
from app.authentication import UserDep

from app.api.routers import (
    auth,
    user,
    group,
    repository,
    credential,
    inventory,
    venv,
    venv_package,
    journal,
)

router = APIRouter()


@router.get("/info")
async def info(current_user: UserDep):
    return {
        "settings": settings,
    }


router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(group.router, prefix="/group", tags=["group"])
router.include_router(repository.router, prefix="/repository", tags=["repository"])
router.include_router(credential.router, prefix="/credential", tags=["credential"])
router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
router.include_router(venv.router, prefix="/venv", tags=["venv"])
router.include_router(
    venv_package.router, prefix="/venv_package", tags=["venv_package"]
)
router.include_router(journal.router, prefix="/journal", tags=["journal"])
