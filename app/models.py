from sqlmodel import Field, Relationship, SQLModel


# group and user link
class Group_User(SQLModel, table=True):
    group_id: int | None = Field(
        default=None, foreign_key="group.id", ondelete="CASCADE", primary_key=True
    )
    user_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE", primary_key=True
    )


# group
class GroupBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)


class Group(GroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(back_populates="groups", link_model=Group_User)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)


class GroupPublic(GroupBase):
    id: int


class GroupPublicWithUsers(GroupPublic):
    users: list["UserPublic"] = []


# user
class UserBase(SQLModel):
    username: str | None = Field(unique=True, index=True, max_length=150)
    name: str | None = Field(default=None, max_length=150)
    is_active: bool = True


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    groups: list[Group] = Relationship(back_populates="users", link_model=Group_User)


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=150)
    is_active: bool = True
    groups: list[int] = []


class UserPublic(UserBase):
    id: int


class UserPublicWithGroups(UserPublic):
    groups: list[GroupPublic] = []


# inventory
class Inventory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=150)


# virtual environment
class Venv(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=150)
