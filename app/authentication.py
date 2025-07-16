from typing import Annotated
import jwt
import uuid

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.config import settings
from app.database import SessionDep
from app.models import TokenData, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_user(session: SessionDep, token: TokenDep) -> User:
    try:
        print(token)
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        print(payload)
        token_data = TokenData(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_user = session.get(User, uuid.UUID(token_data.user_id))
    return db_user
