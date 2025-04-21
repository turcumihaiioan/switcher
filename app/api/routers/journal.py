import uuid

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Journal,
    JournalPublic,
    JournalPublicWithMessages,
)


router = APIRouter()


@router.get("", response_model=list[JournalPublic])
def read_journal(*, session: SessionDep):
    journals = session.exec(select(Journal)).all()
    return journals


@router.get("/{journal_id}", response_model=JournalPublicWithMessages)
def read_journal_by_id(*, session: SessionDep, journal_id: uuid.UUID):
    db_journal = session.get(Journal, journal_id)
    if not db_journal:
        raise HTTPException(
            status_code=404,
            detail="The journal with this id does not exist in the system",
        )
    return db_journal
