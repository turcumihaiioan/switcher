from fastapi import APIRouter
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
