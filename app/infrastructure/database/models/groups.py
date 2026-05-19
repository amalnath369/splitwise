from __future__ import annotations
import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.infrastructure.database.models.base import BaseModel


class GroupModel(BaseModel):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(nullable=False, index=True)
    description: Mapped[str] = mapped_column(nullable=False, default="")
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    members: Mapped[list[GroupMemberModel]] = relationship(
        "GroupMemberModel", back_populates="group", lazy="selectin"
    )


class GroupMemberModel(BaseModel):
    __tablename__ = "group_members"

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
    )

    group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("groups.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    group: Mapped[GroupModel] = relationship("GroupModel", back_populates="members")
