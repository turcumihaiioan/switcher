from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Credential,
    CredentialPublic
)

router = APIRouter()


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
