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


# repository
class RepositoryBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)
    url: str = Field(unique=True, index=True, max_length=150)


class Repository(RepositoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# credential
class CredentialBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)


class Credential(RepositoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# inventory
class Inventory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=150)


# virtual environment
class VenvBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)


class Venv(VenvBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    packages: list["Venv_Package"] = Relationship(
        back_populates="venv", cascade_delete=True
    )


class VenvCreate(VenvBase):
    pass


class VenvUpdate(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)


class VenvPublic(VenvBase):
    id: int


class VenvPublicWithPackages(VenvPublic):
    packages: list["Venv_PackagePublic"] = []


# virtual environment package
class Venv_PackageBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)
    version: str | None = Field(default=None, max_length=150)


class Venv_Package(Venv_PackageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    venv_id: int = Field(foreign_key="venv.id", nullable=False, ondelete="CASCADE")
    venv: Venv | None = Relationship(back_populates="packages")


class Venv_PackageCreate(Venv_PackageBase):
    pass


class Venv_PackagePublic(Venv_PackageBase):
    id: int
