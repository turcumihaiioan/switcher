from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Credential,
    CredentialCreate,
    CredentialPublic,
    CredentialUpdate,
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


@router.patch("/{credential_id}", response_model=CredentialPublic)
def update_credential(
    *, session: SessionDep, credential_id: int, credential: CredentialUpdate
):
    db_credential = session.get(Credential, credential_id)
    if not db_credential:
        raise HTTPException(
            status_code=404,
            detail="The credential with this id does not exist in the system",
        )
    credential_data = credential.model_dump(exclude_unset=True)
    for key, value in credential_data.items():
        if key == "name":
          statement = select(Credential).where(Credential.id != credential_id, Credential.name == value)
          db_credential_name = session.exec(statement).first()
          print (db_credential_name)
          if db_credential_name:
            raise HTTPException(
                status_code=404,
                detail="The credential with this name already exists in the system",
            )
        setattr(db_credential, key, value)
    session.add(db_credential)
    session.commit()
    session.refresh(db_credential)
    return db_credential
