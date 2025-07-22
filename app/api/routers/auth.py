from sqlmodel import select
from typing import Annotated

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.database import SessionDep
from app.models import User, Token
from app.security import create_token

router = APIRouter()


@router.post("/token")
def create_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    statement = select(User).where(User.username == form_data.username)
    db_user = session.exec(statement).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not db_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    token_expires = timedelta(settings.token_expire_minutes)
    token = create_token(data={"user_id": str(db_user.id)}, expires_delta=token_expires)
    return Token(access_token=token)
