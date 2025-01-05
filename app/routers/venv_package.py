from fastapi import APIRouter
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Venv_Package,
    Venv_PackagePublic,
)

router = APIRouter()


@router.get("", response_model=list[Venv_PackagePublic])
def read_venv_package(*, session: SessionDep):
    venv_packages = session.exec(select(Venv_Package)).all()
    return venv_packages
