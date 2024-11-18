from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models.group import (
    Group,
    GroupCreate,
    GroupPublic,
)

router = APIRouter()


@router.post("", response_model=GroupPublic)
def create_group(*, session: SessionDep, group: GroupCreate):
    statement = select(Group).where(Group.name == group.name)
    db_group = session.exec(statement).first()
    if db_group:
        raise HTTPException(
            status_code=400,
            detail="The group with this name already exists in the system",
        )
    db_group = Group.model_validate(group)
    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return db_group


@router.get("", response_model=list[GroupPublic])
def read_group(*, session: SessionDep):
    groups = session.exec(select(Group)).all()
    return groups
