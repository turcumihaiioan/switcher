from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    User,
    UserCreate,
    UserPublic,
    UserUpdate,
)

router = APIRouter()


@router.post("/", response_model=UserPublic)
def create_user(*, session: SessionDep, user: UserCreate):
    statement = select(User).where(User.username == user.username)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserPublic])
def read_user(*, session: SessionDep):
    users = session.exec(select(User)).all()
    return users


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(*, session: SessionDep, user_id: int, user: UserUpdate):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(session: SessionDep, user_id: int):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    session.delete(db_user)
    session.commit()
    return {"ok": True}
