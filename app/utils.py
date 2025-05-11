import uuid
import subprocess

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
        raise Exception(
            f"The journal with this id does not exist in the system: {journal_message.journal_id}"
        )
    db_journal_message = Journal_Message.model_validate(journal_message)
    session.add(db_journal_message)
    session.commit()


def run_ansible_playbook(
    *,
    session=Session,
    playbook: str,
    options: dict,
    journal_id: uuid.UUID,
):
    command = ["ansible-playbook"]
    for key, value in options.items():
        if key == "extra_vars":
            command.append("--extra-vars")
            command.append(f"{value}")
        if key == "inventory":
            command.append("--inventory")
            command.append(value)
        if key == "tags":
            command.append("--tags")
            command.append(value)
    command.append(playbook)
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as e:
        print(f"The subprocess module encountered an error:\n{e}")
        return
    if process.stdout is not None:
        for line in iter(process.stdout.readline, ""):
            try:
                create_journal_message(
                    session=session,
                    journal_message=(
                        Journal_MessageCreate(
                            journal_id=journal_id, message=line.rstrip()
                        )
                    ),
                )
            except Exception as e:
                print(f"The create_journal_message function encountered an error:\n{e}")
                return
        process.stdout.close()
    return_code = process.wait()
    print(f"The subprocess module finished with return code: {return_code}")
