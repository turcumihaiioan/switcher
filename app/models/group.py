from sqlmodel import Field, SQLModel


class GroupBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)


class Group(GroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(SQLModel):
    name: str = Field(unique=True, index=True, max_length=150)


class GroupPublic(GroupBase):
    id: int
