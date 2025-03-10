import uuid

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Venv,
    Venv_Package,
    Venv_PackageCreate,
    Venv_PackagePublic,
    Venv_PackagePublicWithVenv,
    Venv_PackageUpdate,
)

router = APIRouter()


@router.post("", response_model=Venv_PackagePublic)
def create_venv_package(*, session: SessionDep, venv_package: Venv_PackageCreate):
    statement = select(Venv_Package).where(
        Venv_Package.name == venv_package.name,
        Venv_Package.venv_id == venv_package.venv_id,
    )
    db_venv_package = session.exec(statement).first()
    if db_venv_package:
        raise HTTPException(
            status_code=400,
            detail="The venv package with this name and venv_id already exists in the system",
        )
    statement = select(Venv).where(Venv.id == venv_package.venv_id)
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


@router.get("/{venv_package_id}", response_model=Venv_PackagePublicWithVenv)
def read_venv_package_by_id(*, session: SessionDep, venv_package_id: uuid.UUID):
    db_venv_package = session.get(Venv_Package, venv_package_id)
    if not db_venv_package:
        raise HTTPException(
            status_code=404,
            detail="The venv package with this id does not exist in the system",
        )
    return db_venv_package


@router.patch("/{venv_package_id}", response_model=Venv_PackagePublic)
def update_venv_package(
    *, session: SessionDep, venv_package_id: uuid.UUID, venv_package: Venv_PackageUpdate
):
    db_venv_package = session.get(Venv_Package, venv_package_id)
    if not db_venv_package:
        raise HTTPException(
            status_code=404,
            detail="The venv package with this id does not exist in the system",
        )
    venv_package_data = venv_package.model_dump(exclude_unset=True)
    for key, value in venv_package_data.items():
        setattr(db_venv_package, key, value)
    session.add(db_venv_package)
    session.commit()
    session.refresh(db_venv_package)
    return db_venv_package


@router.delete("/{venv_package_id}")
def delete_venv_package(session: SessionDep, venv_package_id: uuid.UUID):
    db_venv_package = session.get(Venv_Package, venv_package_id)
    if not db_venv_package:
        raise HTTPException(
            status_code=404,
            detail="The venv package with this id does not exist in the system",
        )
    session.delete(db_venv_package)
    session.commit()
    return {"ok": True}
