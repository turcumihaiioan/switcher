from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Repository,
    RepositoryPublic,
)

router = APIRouter()


@router.get("", response_model=list[RepositoryPublic])
def read_repository(*, session: SessionDep):
    repositories = session.exec(select(Repository)).all()
    return repositories


@router.get("/{repository_id}", response_model=RepositoryPublic)
def read_repository_by_id(*, session: SessionDep, repository_id: int):
    db_repository = session.get(Repository, repository_id)
    if not db_repository:
        raise HTTPException(
            status_code=404,
            detail="The repository with this id does not exist in the system",
        )
    return db_repository
