from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


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
    name: str = Field(index=True, max_length=150, min_length=1, unique=True)


class Group(GroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(back_populates="groups", link_model=Group_User)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(SQLModel):
    name: str = Field(index=True, max_length=150, min_length=1, unique=True)


class GroupPublic(GroupBase):
    id: int


class GroupPublicWithUsers(GroupPublic):
    users: list["UserPublic"] = []


# user
class UserBase(SQLModel):
    is_active: bool = True
    name: str | None = Field(default=None, max_length=150, min_length=1)
    username: str | None = Field(index=True, max_length=150, min_length=1, unique=True)


class User(UserBase, table=True):
    groups: list[Group] = Relationship(back_populates="users", link_model=Group_User)
    id: int | None = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    groups: list[int] = []
    is_active: bool = True
    name: str | None = Field(default=None, max_length=150, min_length=1)


class UserPublic(UserBase):
    id: int


class UserPublicWithGroups(UserPublic):
    groups: list[GroupPublic] = []


# repository
class RepositoryBase(SQLModel):
    name: str = Field(index=True, max_length=150, min_length=1, unique=True)
    url: str = Field(index=True, max_length=150, min_length=1, unique=True)


class Repository(RepositoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# credential
class CredentialBase(SQLModel):
    name: str = Field(index=True, max_length=150, min_length=1, unique=True)


class Credential(RepositoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# inventory
class Inventory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=150, min_length=1, unique=True)


# virtual environment
class VenvBase(SQLModel):
    name: str = Field(index=True, max_length=150, min_length=1, unique=True)


class Venv(VenvBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    packages: list["Venv_Package"] = Relationship(
        back_populates="venv", cascade_delete=True
    )


class VenvCreate(VenvBase):
    pass


class VenvUpdate(SQLModel):
    name: str = Field(index=True, max_length=150, min_length=1, unique=True)


class VenvPublic(VenvBase):
    id: int


class VenvPublicWithPackages(VenvPublic):
    packages: list["Venv_PackagePublic"] = []


# virtual environment package
class Venv_PackageBase(SQLModel):
    name: str = Field(index=True, max_length=150, min_length=1)
    version: str | None = Field(default=None, max_length=150)


class Venv_Package(Venv_PackageBase, table=True):
    __table_args__ = (UniqueConstraint("name", "venv_id"),)
    id: int | None = Field(default=None, primary_key=True)
    venv: Venv = Relationship(back_populates="packages")
    venv_id: int = Field(foreign_key="venv.id", nullable=False, ondelete="CASCADE")


class Venv_PackageCreate(Venv_PackageBase):
    venv_id: int | None


class Venv_PackageUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=150, min_length=1)
    version: str | None = Field(default=None, max_length=150)


class Venv_PackagePublic(Venv_PackageBase):
    id: int


class Venv_PackagePublicWithVenv(Venv_PackagePublic):
    venv: Venv
