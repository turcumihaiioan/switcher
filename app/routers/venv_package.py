from fastapi import APIRouter
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Venv_Package,
    Venv_PackageCreate,
    Venv_PackagePublic,
)

router = APIRouter()


@router.post("", response_model=Venv_PackagePublic)
def create_venv_package(*, session: SessionDep, venv_package: Venv_PackageCreate):
    db_venv_package = Venv_Package.model_validate(venv_package)
    session.add(db_venv_package)
    session.commit()
    session.refresh(db_venv_package)
    return db_venv_package


@router.get("", response_model=list[Venv_PackagePublic])
def read_venv_package(*, session: SessionDep):
    venv_packages = session.exec(select(Venv_Package)).all()
    return venv_packages
