from sqlmodel import Field, SQLModel


class Group_User(SQLModel, table=True):
    group_id: int | None = Field(default=None, foreign_key="group.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
