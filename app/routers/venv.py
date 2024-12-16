from fastapi import APIRouter
from sqlmodel import select

from app.database import SessionDep
from app.models import Venv

router = APIRouter()


@router.get("", response_model=list[Venv])
def read_venv(*, session: SessionDep):
    venvs = session.exec(select(Venv)).all()
    return venvs
