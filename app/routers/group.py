from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Group,
    GroupCreate,
    GroupPublic,
    GroupUpdate,
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


@router.get("/{group_id}", response_model=GroupPublic)
def read_group_by_id(*, session: SessionDep, group_id: int):
    db_group = session.get(Group, group_id)
    if not db_group:
        raise HTTPException(
            status_code=404,
            detail="The group with this id does not exist in the system",
        )
    return db_group


@router.patch("/{group_id}", response_model=GroupPublic)
def update_group(*, session: SessionDep, group_id: int, group: GroupUpdate):
    db_group = session.get(Group, group_id)
    if not db_group:
        raise HTTPException(
            status_code=404,
            detail="The group with this id does not exist in the system",
        )
    group_data = group.model_dump(exclude_unset=True)
    for key, value in group_data.items():
        setattr(db_group, key, value)
    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return db_group


@router.delete("/{group_id}")
def delete_group(session: SessionDep, group_id: int):
    db_group = session.get(Group, group_id)
    if not db_group:
        raise HTTPException(
            status_code=404,
            detail="The group with this id does not exist in the system",
        )
    session.delete(db_group)
    session.commit()
    return {"ok": True}
