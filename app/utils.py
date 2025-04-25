from sqlmodel import Session
from app.models import (
    Journal,
    JournalCreate,
)


def create_journal(*, session: Session, journal: JournalCreate):
    db_journal = Journal.model_validate(journal)
    session.add(db_journal)
    session.commit()
    session.refresh(db_journal)
    return db_journal
