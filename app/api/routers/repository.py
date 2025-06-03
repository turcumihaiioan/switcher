import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlmodel import select

from app.config import settings
from app.database import SessionDep
from app.models import (
    JournalCreate,
    Repository,
    RepositoryCreate,
    RepositoryPublic,
    RepositoryPublicWithJournal,
    RepositoryPublicWithLinks,
    RepositoryUpdate,
    Venv,
    Venv_Package,
)
from app import utils

router = APIRouter()


@router.post("", response_model=RepositoryPublicWithJournal)
def create_repository(
    *,
    session: SessionDep,
    background_tasks: BackgroundTasks,
    repository: RepositoryCreate,
):
    statement = select(Repository).where(Repository.name == repository.name)
    db_repository = session.exec(statement).first()
    if db_repository:
        raise HTTPException(
            status_code=400,
            detail="The repository with this name already exists in the system",
        )
    db_venv = session.get(Venv, repository.venv_id)
    if not db_venv:
        raise HTTPException(
            status_code=400,
            detail="The venv with this id(venv_id) does not exist in the system",
        )
    db_repository = Repository.model_validate(repository)
    session.add(db_repository)
    db_journal_id = utils.create_journal(
        session=session, journal=(JournalCreate(unit_id=db_repository.id))
    )
    background_tasks.add_task(
        utils.run_ansible_playbook,
        session=session,
        venv_directory=str(Path(settings.venv_dir) / str(db_repository.venv_id)),
        playbook="app/playbooks/repository.yml",
        options={
            "extra_vars": {
                "repository_directory": str(
                    Path(settings.repository_dir).resolve() / str(db_repository.id)
                ),
            },
            "inventory": "localhost,",
            "tags": "create",
        },
        journal_id=db_journal_id,
    )
    session.commit()
    session.refresh(db_repository)
    db_repository_journal = RepositoryPublicWithJournal(
        name=db_repository.name,
        url=db_repository.url,
        id=db_repository.id,
        journal_id=db_journal_id,
    )
    return db_repository_journal


@router.get("", response_model=list[RepositoryPublic])
def read_repository(*, session: SessionDep):
    repositories = session.exec(select(Repository)).all()
    return repositories


@router.get("/{repository_id}", response_model=RepositoryPublicWithLinks)
def read_repository_by_id(*, session: SessionDep, repository_id: uuid.UUID):
    db_repository = session.get(Repository, repository_id)
    if not db_repository:
        raise HTTPException(
            status_code=404,
            detail="The repository with this id does not exist in the system",
        )
    return db_repository


@router.patch("/{repository_id}", response_model=RepositoryPublicWithLinks)
def update_repository(
    *, session: SessionDep, repository_id: uuid.UUID, repository: RepositoryUpdate
):
    db_repository = session.get(Repository, repository_id)
    if not db_repository:
        raise HTTPException(
            status_code=404,
            detail="The repository with this id does not exist in the system",
        )
    repository_data = repository.model_dump(exclude_unset=True)
    for key, value in repository_data.items():
        if key == "name":
            statement = select(Repository).where(
                Repository.id != repository_id, Repository.name == value
            )
            db_repository_name = session.exec(statement).first()
            if db_repository_name:
                raise HTTPException(
                    status_code=404,
                    detail="The repository with this name already exists in the system",
                )
        if key == "venv_id":
            db_venv = session.get(Venv, value)
            if not db_venv:
                raise HTTPException(
                    status_code=400,
                    detail="The venv with this id(venv_id) does not exist in the system",
                )
        setattr(db_repository, key, value)
    session.add(db_repository)
    session.commit()
    session.refresh(db_repository)
    return db_repository


@router.delete("/{repository_id}")
def delete_repository(
    *, session: SessionDep, background_tasks: BackgroundTasks, repository_id: uuid.UUID
):
    db_repository = session.get(Repository, repository_id)
    if not db_repository:
        raise HTTPException(
            status_code=404,
            detail="The repository with this id does not exist in the system",
        )
    session.delete(db_repository)
    db_journal_id = utils.create_journal(
        session=session, journal=(JournalCreate(unit_id=db_repository.id))
    )
    background_tasks.add_task(
        utils.run_ansible_playbook,
        session=session,
        venv_directory=str(Path(settings.venv_dir) / str(db_repository.venv_id)),
        playbook="app/playbooks/repository.yml",
        options={
            "extra_vars": {
                "repository_directory": str(
                    Path(settings.repository_dir).resolve() / str(db_repository.id)
                ),
            },
            "inventory": "localhost,",
            "tags": "delete",
        },
        journal_id=db_journal_id,
    )
    session.commit()
    db_repository_journal = RepositoryPublicWithJournal(
        name=db_repository.name,
        url=db_repository.url,
        id=db_repository.id,
        journal_id=db_journal_id,
    )
    return db_repository_journal


@router.post("/{repository_id}/install")
def install_repository_by_id(
    *, session: SessionDep, background_tasks: BackgroundTasks, repository_id: uuid.UUID
):
    db_repository = session.get(Repository, repository_id)
    if not db_repository:
        raise HTTPException(
            status_code=404,
            detail="The repository with this id does not exist in the system",
        )
    statement = select(Venv_Package.name).where(
        Venv_Package.venv_id == db_repository.venv_id
    )
    db_venv_packages = session.exec(statement).all()
    if len(db_venv_packages) == 0:
        raise HTTPException(
            status_code=404,
            detail="The linked venv does not have any packages",
        )
    if "ansible" not in db_venv_packages:
        raise HTTPException(
            status_code=404,
            detail="The linked venv does not have the ansible package",
        )
    db_journal_id = utils.create_journal(
        session=session, journal=(JournalCreate(unit_id=db_repository.id))
    )
    background_tasks.add_task(
        utils.run_ansible_playbook,
        session=session,
        venv_directory=str(Path(settings.venv_dir) / str(db_repository.venv_id)),
        playbook="app/playbooks/repository.yml",
        options={
            "extra_vars": {
                "repository_directory": str(
                    Path(settings.repository_dir).resolve() / str(db_repository.id)
                ),
                "repository_url": str(db_repository.url),
            },
            "inventory": "localhost,",
            "tags": "install",
        },
        journal_id=db_journal_id,
    )
    return {"ok": True, "journal_id": db_journal_id}


@router.post("/{repository_id}/uninstall")
def uninstall_repository_by_id(
    *, session: SessionDep, background_tasks: BackgroundTasks, repository_id: uuid.UUID
):
    db_repository = session.get(Repository, repository_id)
    if not db_repository:
        raise HTTPException(
            status_code=404,
            detail="The repository with this id does not exist in the system",
        )
    db_journal_id = utils.create_journal(
        session=session, journal=(JournalCreate(unit_id=db_repository.id))
    )
    background_tasks.add_task(
        utils.run_ansible_playbook,
        session=session,
        venv_directory=str(Path(settings.venv_dir) / str(db_repository.venv_id)),
        playbook="app/playbooks/repository.yml",
        options={
            "extra_vars": {
                "repository_directory": str(
                    Path(settings.repository_dir).resolve() / str(db_repository.id)
                ),
            },
            "inventory": "localhost,",
            "tags": "uninstall",
        },
        journal_id=db_journal_id,
    )
    return {"ok": True, "journal_id": db_journal_id}
