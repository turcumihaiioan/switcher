from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Credential,
    CredentialCreate,
    CredentialPublic,
)

router = APIRouter()


@router.post("", response_model=CredentialPublic)
def create_credential(*, session: SessionDep, credential: CredentialCreate):
    statement = select(Credential).where(Credential.name == credential.name)
    db_credential = session.exec(statement).first()
    if db_credential:
        raise HTTPException(
            status_code=400,
            detail="The credential with this name already exists in the system",
        )
    db_credential = Credential.model_validate(credential)
    session.add(db_credential)
    session.commit()
    session.refresh(db_credential)
    return db_credential


@router.get("", response_model=list[CredentialPublic])
def read_credential(*, session: SessionDep):
    credentials = session.exec(select(Credential)).all()
    return credentials


@router.get("/{credential_id}", response_model=CredentialPublic)
def read_credential_by_id(*, session: SessionDep, credential_id: int):
    db_credential = session.get(Credential, credential_id)
    if not db_credential:
        raise HTTPException(
            status_code=404,
            detail="The credential with this id does not exist in the system",
        )
    return db_credential
