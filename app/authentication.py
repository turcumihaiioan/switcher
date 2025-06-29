from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login/access-token")

TokenDep = Annotated[str, Depends(oauth2_scheme)]
