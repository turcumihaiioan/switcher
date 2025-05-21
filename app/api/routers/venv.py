import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlmodel import select

from app.config import settings
from app.database import SessionDep
from app.models import (
    JournalCreate,
    Venv,
    VenvCreate,
    VenvPublic,
    VenvPublicWithJournal,
    VenvPublicWithLinks,
    VenvUpdate,
    Venv_Package,
)
from app import utils


router = APIRouter()


@router.post("", response_model=VenvPublicWithJournal)
def create_venv(
    *, session: SessionDep, background_tasks: BackgroundTasks, venv: VenvCreate
):
    statement = select(Venv).where(Venv.name == venv.name)
    db_venv = session.exec(statement).first()
    if db_venv:
        raise HTTPException(
            status_code=400,
            detail="The venv with this name already exists in the system",
        )
    db_venv = Venv.model_validate(venv)
    session.add(db_venv)
    db_journal_id = utils.create_journal(
        session=session, journal=(JournalCreate(unit_id=db_venv.id))
    )
    background_tasks.add_task(
        utils.run_ansible_playbook,
        session=session,
        playbook="app/playbooks/venv.yml",
        options={
            "extra_vars": {
                "venv_directory": str(
                    Path(settings.venv_dir).resolve() / str(db_venv.id)
                ),
            },
            "inventory": "localhost,",
            "tags": "create",
        },
        journal_id=db_journal_id,
    )
    session.commit()
    session.refresh(db_venv)
    db_venv_journal = VenvPublicWithJournal(
        name=db_venv.name, id=db_venv.id, journal_id=db_journal_id
    )
    return db_venv_journal


@router.get("", response_model=list[VenvPublic])
def read_venv(*, session: SessionDep):
    venvs = session.exec(select(Venv)).all()
    return venvs


@router.get("/{venv_id}", response_model=VenvPublicWithLinks)
def read_venv_by_id(*, session: SessionDep, venv_id: uuid.UUID):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    return db_venv


@router.patch("/{venv_id}", response_model=VenvPublic)
def update_venv(*, session: SessionDep, venv_id: uuid.UUID, venv: VenvUpdate):
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
def delete_venv(
    *, session: SessionDep, background_tasks: BackgroundTasks, venv_id: uuid.UUID
):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    if db_venv.repositories:
        repository_names = set(str(i.id) for i in db_venv.repositories)
        if len(repository_names) == 1:
            links_repositories_detail = (
                "The repository with id "
                + ", ".join(repository_names)
                + " is linked to this venv"
            )
        else:
            links_repositories_detail = (
                "The repositories with ids "
                + ", ".join(repository_names)
                + " are linked to this venv"
            )
        raise HTTPException(
            status_code=409,
            detail=links_repositories_detail,
        )
    session.delete(db_venv)
    db_journal_id = utils.create_journal(
        session=session, journal=(JournalCreate(unit_id=db_venv.id))
    )
    background_tasks.add_task(
        utils.run_ansible_playbook,
        session=session,
        playbook="app/playbooks/venv.yml",
        options={
            "extra_vars": {
                "venv_directory": str(
                    Path(settings.venv_dir).resolve() / str(db_venv.id)
                ),
            },
            "inventory": "localhost,",
            "tags": "delete",
        },
        journal_id=db_journal_id,
    )
    session.commit()
    return {"ok": True, "journal_id": db_journal_id}


@router.post("/{venv_id}/install")
def install_venv_by_id(
    *, session: SessionDep, background_tasks: BackgroundTasks, venv_id: uuid.UUID
):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    statement = select(Venv_Package).where(Venv_Package.venv_id == venv_id)
    db_venv_package = session.exec(statement).all()
    if len(db_venv_package) == 0:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not have any packages to install",
        )
    db_venv_packages = []
    for item in db_venv_package:
        if item.version is not None:
            db_venv_packages.append(f"{item.name}=={item.version}")
        else:
            db_venv_packages.append(f"{item.name}")
    db_journal_id = utils.create_journal(
        session=session, journal=(JournalCreate(unit_id=db_venv.id))
    )
    background_tasks.add_task(
        utils.run_ansible_playbook,
        session=session,
        playbook="app/playbooks/venv.yml",
        options={
            "extra_vars": {
                "venv_directory": str(
                    Path(settings.venv_dir).resolve() / str(db_venv.id)
                ),
                "venv_package": db_venv_packages,
            },
            "inventory": "localhost,",
            "tags": "install",
        },
        journal_id=db_journal_id,
    )
    return {"ok": True, "journal_id": db_journal_id}


@router.post("/{venv_id}/uninstall")
def uninstall_venv_by_id(
    *, session: SessionDep, background_tasks: BackgroundTasks, venv_id: uuid.UUID
):
    db_venv = session.get(Venv, venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=404,
            detail="The venv with this id does not exist in the system",
        )
    db_journal_id = utils.create_journal(
        session=session, journal=(JournalCreate(unit_id=db_venv.id))
    )
    background_tasks.add_task(
        utils.run_ansible_playbook,
        session=session,
        playbook="app/playbooks/venv.yml",
        options={
            "extra_vars": {
                "venv_directory": str(
                    Path(settings.venv_dir).resolve() / str(db_venv.id)
                ),
            },
            "inventory": "localhost,",
            "tags": "uninstall",
        },
        journal_id=db_journal_id,
    )
    return {"ok": True, "journal_id": db_journal_id}
