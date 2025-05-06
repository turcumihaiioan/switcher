from fastapi import HTTPException
from sqlmodel import Session
from app.models import (
    Journal,
    JournalCreate,
    Journal_Message,
    Journal_MessageCreate,
)


def create_journal(*, session: Session, journal: JournalCreate):
    db_journal = Journal.model_validate(journal)
    session.add(db_journal)
    session.commit()
    session.refresh(db_journal)
    return db_journal.id


def create_journal_message(*, session: Session, journal_message: Journal_MessageCreate):
    db_journal = session.get(Journal, journal_message.journal_id)
    if not db_journal:
        raise HTTPException(
            status_code=400,
            detail="The journal with this id does not exists in the system",
        )
    db_journal_message = Journal_Message.model_validate(journal_message)
    session.add(db_journal_message)
    session.commit()
