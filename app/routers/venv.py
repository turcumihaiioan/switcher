from fastapi import APIRouter
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Venv,
    VenvPublic,
)

router = APIRouter()


@router.get("", response_model=list[VenvPublic])
def read_venv(*, session: SessionDep):
    venvs = session.exec(select(Venv)).all()
    return venvs
