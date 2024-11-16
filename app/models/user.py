from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str | None = Field(unique=True, index=True, max_length=150)
    name: str | None = Field(default=None, max_length=150)
    is_active: bool = True


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=150)
    is_active: bool = True


class UserPublic(UserBase):
    id: int
