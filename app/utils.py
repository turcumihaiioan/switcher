import uuid
import subprocess
import json

from sqlmodel import Session
from app.models import (
    Journal,
    JournalCreate,
    JournalUpdate,
    Journal_Message,
    Journal_MessageCreate,
)


def create_journal(*, session: Session, journal: JournalCreate) -> uuid.UUID:
    db_journal = Journal.model_validate(journal)
    session.add(db_journal)
    session.commit()
    session.refresh(db_journal)
    return db_journal.id


def update_journal(
    *, session: Session, journal_id: uuid.UUID, journal: JournalUpdate
) -> None:
    db_journal = session.get(Journal, journal_id)
    journal_data = journal.model_dump(exclude_unset=True)
    for key, value in journal_data.items():
        setattr(db_journal, key, value)
    session.add(db_journal)
    session.commit()


def create_journal_message(
    *, session: Session, journal_message: Journal_MessageCreate
) -> None:
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
    venv_directory: str | None = None,
    playbook: str,
    options: dict,
    journal_id: uuid.UUID,
) -> None:
    update_journal(
        session=session,
        journal_id=journal_id,
        journal=(JournalUpdate(active="activating")),
    )
    if venv_directory is not None:
        command = [f"{venv_directory}/bin/ansible-playbook"]
    else:
        command = ["ansible-playbook"]
    for key, value in options.items():
        if key == "extra_vars":
            command.extend(["--extra-vars", json.dumps(value)])
        if key == "inventory":
            command.extend(["--inventory", value])
        if key == "tags":
            command.extend(["--tags", value])
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
        print(f"The run_ansible_playbook subprocess module encountered an error:\n{e}")
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
    print(
        f"The run_ansible_playbook subprocess module finished with return code: {return_code}"
    )
