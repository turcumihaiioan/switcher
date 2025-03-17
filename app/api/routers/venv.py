import subprocess
import uuid

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.config import settings
from app.database import SessionDep
from app.models import (
    Venv,
    VenvCreate,
    VenvPublic,
    VenvPublicWithPackages,
    VenvUpdate,
    Venv_Package,
)


router = APIRouter()


@router.post("", response_model=VenvPublic)
async def create_venv(*, session: SessionDep, venv: VenvCreate):
    statement = select(Venv).where(Venv.name == venv.name)
    db_venv = session.exec(statement).first()
    if db_venv:
        raise HTTPException(
            status_code=400,
            detail="The venv with this name already exists in the system",
        )
    db_venv = Venv.model_validate(venv)
    session.add(db_venv)
    try:
        subprocess.run(
            [
                "python",
                "-m",
                "venv",
                "--upgrade-deps",
                f"{settings.venv_dir}/{db_venv.id}",
            ],
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"The subprocess encountered an error :\n{e.stderr}",
        )
    session.commit()
    session.refresh(db_venv)
    return db_venv


@router.get("", response_model=list[VenvPublic])
def read_venv(*, session: SessionDep):
    venvs = session.exec(select(Venv)).all()
    return venvs


@router.get("/{venv_id}", response_model=VenvPublicWithPackages)
def read_venv_by_id(*, session: SessionDep, venv_id: uuid.UUID):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    return db_venv


@router.patch("/{venv_id}", response_model=VenvPublic)
def update_venv(*, session: SessionDep, venv_id: uuid.UUID, venv: VenvUpdate):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    venv_data = venv.model_dump(exclude_unset=True)
    for key, value in venv_data.items():
        setattr(db_venv, key, value)
    session.add(db_venv)
    session.commit()
    session.refresh(db_venv)
    return db_venv


@router.delete("/{venv_id}")
def delete_venv(session: SessionDep, venv_id: uuid.UUID):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    session.delete(db_venv)
    try:
        subprocess.run(
            ["rm", "-r", "-f", f"{settings.venv_dir}/{db_venv.id}"],
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"The subprocess encountered an error :\n{e.stderr}",
        )
    session.commit()
    return {"ok": True}


@router.post("/{venv_id}/install")
def install_venv_by_id(*, session: SessionDep, venv_id: uuid.UUID):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    statement = select(Venv_Package).where(Venv_Package.venv_id == venv_id)
    db_venv_package = session.exec(statement).all()
    if len(db_venv_package) == 0:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not have any packages to install",
        )
    db_venv_packages = []
    for item in db_venv_package:
        if item.version is not None:
            db_venv_packages.append(f"{item.name}=={item.version}")
        else:
            db_venv_packages.append(f"{item.name}")
    try:
        subprocess.run(
            [
                f"{settings.venv_dir}/{db_venv.id}/bin/python",
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
            ]
            + db_venv_packages,
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"The subprocess encountered an error :\n{e.stderr}",
        )
    return {"ok": True}


@router.post("/{venv_id}/uninstall")
def uninstall_venv_by_id(*, session: SessionDep, venv_id: uuid.UUID):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    try:
        subprocess.run(
            [
                "python",
                "-m",
                "venv",
                "--clear",
                "--upgrade-deps",
                f"{settings.venv_dir}/{db_venv.id}",
            ],
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"The subprocess encountered an error :\n{e.stderr}",
        )
    return {"ok": True}
