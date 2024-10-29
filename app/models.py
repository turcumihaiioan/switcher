from sqlmodel import Field, SQLModel

class UserBase(SQLModel):
    username: str | None = Field(unique=True, index=True, max_length=150)
    name: str | None = Field(default=None, max_length=150)
    is_active: bool = True

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class UserCreate(UserBase):
    pass

class UserPublic(UserBase):
    id: int

class GroupBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)

class Group(GroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class Group_User(SQLModel, table=True):
    group_id: int | None = Field(default=None, foreign_key="group.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
