from datetime import datetime
import uuid

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
    name: str = Field(index=True, max_length=128, min_length=1, unique=True)


class Group(GroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(back_populates="groups", link_model=Group_User)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(SQLModel):
    name: str = Field(index=True, max_length=128, min_length=1, unique=True)


class GroupPublic(GroupBase):
    id: int


class GroupPublicWithUsers(GroupPublic):
    users: list["UserPublic"] = []


# user
class UserBase(SQLModel):
    is_active: bool = True
    name: str | None = Field(default=None, max_length=128, min_length=1)
    username: str | None = Field(index=True, max_length=128, min_length=1, unique=True)


class User(UserBase, table=True):
    groups: list[Group] = Relationship(back_populates="users", link_model=Group_User)
    id: int | None = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    groups: list[int] = []
    is_active: bool = True
    name: str | None = Field(default=None, max_length=128, min_length=1)


class UserPublic(UserBase):
    id: int


class UserPublicWithGroups(UserPublic):
    groups: list[GroupPublic] = []


# journal
class JournalBase(SQLModel):
    unit_id: uuid.UUID = Field(nullable=False)


class Journal(JournalBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    messages: list["Journal_Message"] = Relationship(
        back_populates="journal", cascade_delete=True
    )


class JournalCreate(JournalBase):
    pass


class JournalPublic(JournalBase):
    id: uuid.UUID


class JournalPublicWithMessages(JournalPublic):
    messages: list["Journal_MessagePublic"] = []


class Journal_MessageBase(SQLModel):
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Journal_Message(Journal_MessageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    journal: Journal = Relationship(back_populates="messages")
    journal_id: uuid.UUID = Field(
        foreign_key="journal.id", nullable=False, ondelete="CASCADE"
    )


class Journal_MessagePublic(Journal_MessageBase):
    pass


# repository
class RepositoryBase(SQLModel):
    name: str = Field(index=True, max_length=128, min_length=1, unique=True)
    url: str = Field(index=True, max_length=128, min_length=1)


class Repository(RepositoryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    venv: "Venv" = Relationship(back_populates="repositories")
    venv_id: uuid.UUID = Field(
        foreign_key="venv.id", nullable=False, ondelete="RESTRICT"
    )


class RepositoryCreate(RepositoryBase):
    venv_id: uuid.UUID


class RepositoryUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=128, min_length=1, unique=True)
    url: str | None = Field(default=None, max_length=128, min_length=1)
    venv_id: uuid.UUID | None = Field(default=None)


class RepositoryPublic(RepositoryBase):
    id: uuid.UUID


class RepositoryPublicWithLinks(RepositoryPublic):
    venv_id: uuid.UUID


# credential
class CredentialBase(SQLModel):
    name: str = Field(index=True, max_length=128, min_length=1, unique=True)


class Credential(CredentialBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CredentialCreate(CredentialBase):
    pass


class CredentialPublic(CredentialBase):
    id: int


class CredentialUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=128, min_length=1, unique=True)


# inventory
class InventoryBase(SQLModel):
    name: str = Field(index=True, max_length=128, min_length=1, unique=True)


class Inventory(InventoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class InventoryCreate(InventoryBase):
    pass


class InventoryPublic(InventoryBase):
    id: int


class InventoryUpdate(SQLModel):
    name: str = Field(index=True, max_length=128, min_length=1, unique=True)


# virtual environment
class VenvBase(SQLModel):
    name: str = Field(index=True, max_length=128, min_length=1, unique=True)


class Venv(VenvBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    packages: list["Venv_Package"] = Relationship(
        back_populates="venv", cascade_delete=True
    )
    repositories: list["Repository"] = Relationship(
        back_populates="venv", passive_deletes="all"
    )


class VenvCreate(VenvBase):
    pass


class VenvUpdate(SQLModel):
    name: str = Field(index=True, max_length=128, min_length=1, unique=True)


class VenvPublic(VenvBase):
    id: uuid.UUID


class VenvPublicWithLinks(VenvPublic):
    packages: list["Venv_PackagePublic"] = []
    repositories: list["RepositoryPublic"] = []


class VenvPublicWithJournal(SQLModel):
    name: str
    id: uuid.UUID
    journal_id: uuid.UUID


# virtual environment package
class Venv_PackageBase(SQLModel):
    name: str = Field(index=True, max_length=64, min_length=1)
    version: str | None = Field(
        default=None,
        max_length=32,
        schema_extra=dict(
            pattern=r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$"
        ),
    )


class Venv_Package(Venv_PackageBase, table=True):
    __table_args__ = (UniqueConstraint("name", "venv_id"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    venv: Venv = Relationship(back_populates="packages")
    venv_id: uuid.UUID = Field(
        foreign_key="venv.id", nullable=False, ondelete="CASCADE"
    )


class Venv_PackageCreate(Venv_PackageBase):
    venv_id: uuid.UUID


class Venv_PackageUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=64, min_length=1)
    version: str | None = Field(
        default=None,
        max_length=32,
        schema_extra=dict(
            pattern=r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$"
        ),
    )


class Venv_PackagePublic(Venv_PackageBase):
    id: uuid.UUID


class Venv_PackagePublicWithVenv(Venv_PackagePublic):
    venv: Venv
