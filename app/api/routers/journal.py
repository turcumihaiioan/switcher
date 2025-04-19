from fastapi import APIRouter
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Journal,
    JournalPublic,
)


router = APIRouter()


@router.get("", response_model=list[JournalPublic])
def read_journal(*, session: SessionDep):
    journals = session.exec(select(Journal)).all()
    return journals
