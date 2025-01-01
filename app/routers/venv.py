from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Venv,
    VenvCreate,
    VenvPublic,
    VenvPublicWithPackages,
    VenvUpdate,
)

router = APIRouter()


@router.post("", response_model=VenvPublic)
def create_venv(*, session: SessionDep, venv: VenvCreate):
    statement = select(Venv).where(Venv.name == venv.name)
    db_venv = session.exec(statement).first()
    if db_venv:
        raise HTTPException(
            status_code=400,
            detail="The venv with this name already exists in the system",
        )
    db_venv = Venv.model_validate(venv)
    session.add(db_venv)
    session.commit()
    session.refresh(db_venv)
    return db_venv


@router.get("", response_model=list[VenvPublic])
def read_venv(*, session: SessionDep):
    venvs = session.exec(select(Venv)).all()
    return venvs


@router.get("/{venv_id}", response_model=VenvPublicWithPackages)
def read_venv_by_id(*, session: SessionDep, venv_id: int):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    return db_venv


@router.patch("/{venv_id}", response_model=VenvPublic)
def update_venv(*, session: SessionDep, venv_id: int, venv: VenvUpdate):
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
def delete_venv(session: SessionDep, venv_id: int):
    db_venv= session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    session.delete(db_venv)
    session.commit()
    return {"ok": True}
