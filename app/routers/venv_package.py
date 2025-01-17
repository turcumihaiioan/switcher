from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Venv,
    Venv_Package,
    Venv_PackageCreate,
    Venv_PackagePublic,
)

router = APIRouter()


@router.post("", response_model=Venv_PackagePublic)
def create_venv_package(*, session: SessionDep, venv_package: Venv_PackageCreate):
    statement = select(Venv_Package).where(Venv_Package.name == venv_package.name, Venv_Package.venv_id == venv_package.venv_id )
    db_venv_package = session.exec(statement).first()
    if db_venv_package:
        raise HTTPException(
            status_code=400,
            detail="The venv package with this name and venv_id already exists in the system",
        )
    statement = select(Venv).where(Venv.id  == venv_package.venv_id)
    db_venv = session.exec(statement).first()
    if not db_venv:
        raise HTTPException(
            status_code=400,
            detail="The venv with this id(venv_id) does not exist in the system",
        )
    db_venv_package = Venv_Package.model_validate(venv_package)
    session.add(db_venv_package)
    session.commit()
    session.refresh(db_venv_package)
    return db_venv_package


@router.get("", response_model=list[Venv_PackagePublic])
def read_venv_package(*, session: SessionDep):
    venv_packages = session.exec(select(Venv_Package)).all()
    return venv_packages
