from fastapi import APIRouter
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
