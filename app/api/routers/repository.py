import os
import uuid

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.config import settings
from app.database import SessionDep
from app.models import (
    Repository,
    RepositoryCreate,
    RepositoryPublic,
    RepositoryUpdate,
)

router = APIRouter()


@router.post("", response_model=RepositoryPublic)
def create_repository(*, session: SessionDep, repository: RepositoryCreate):
    statement = select(Repository).where(Repository.name == repository.name)
    db_repository = session.exec(statement).first()
    if db_repository:
        raise HTTPException(
            status_code=400,
            detail="The repository with this name already exists in the system",
        )
    db_repository = Repository.model_validate(repository)

    session.add(db_repository)
    try:
        os.makedirs(f"{settings.repository_dir}/{db_repository.id}")
    except OSError as e:
        raise HTTPException(
            status_code=500,
            detail=f"The os module encountered an error :\n{e.strerror}",
        )
    session.commit()
    session.refresh(db_repository)
    return db_repository


@router.get("", response_model=list[RepositoryPublic])
def read_repository(*, session: SessionDep):
    repositories = session.exec(select(Repository)).all()
    return repositories


@router.get("/{repository_id}", response_model=RepositoryPublic)
def read_repository_by_id(*, session: SessionDep, repository_id: uuid.UUID):
    db_repository = session.get(Repository, repository_id)
    if not db_repository:
        raise HTTPException(
            status_code=404,
            detail="The repository with this id does not exist in the system",
        )
    return db_repository


@router.patch("/{repository_id}", response_model=RepositoryPublic)
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
        setattr(db_repository, key, value)
    session.add(db_repository)
    session.commit()
    session.refresh(db_repository)
    return db_repository


@router.delete("/{repository_id}")
def delete_repository(session: SessionDep, repository_id: uuid.UUID):
    db_repository = session.get(Repository, repository_id)
    if not db_repository:
        raise HTTPException(
            status_code=404,
            detail="The repository with this id does not exist in the system",
        )
    session.delete(db_repository)
    session.commit()
    return {"ok": True}
