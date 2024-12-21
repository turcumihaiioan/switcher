from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Venv,
    VenvCreate,
    VenvPublic,
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
