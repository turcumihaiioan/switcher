import base64
import bcrypt
import binascii
import jwt
import typing

from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from passlib.context import CryptContext

from app.config import settings


bcrypt.__about__ = bcrypt  # type: ignore[attr-defined]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Fernet_AES_256_CBC(Fernet):
    def __init__(
        self,
        key: bytes | str,
        backend: typing.Any = None,
    ) -> None:
        try:
            key = base64.urlsafe_b64decode(key)
        except binascii.Error as exc:
            raise ValueError(
                "Fernet key must be 64 url-safe base64-encoded bytes."
            ) from exc
        if len(key) != 64:
            raise ValueError("Fernet key must be 64 url-safe base64-encoded bytes.")

        self._signing_key = key[:32]
        self._encryption_key = key[32:]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt
