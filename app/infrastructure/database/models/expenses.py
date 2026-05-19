from __future__ import annotations
import uuid

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.infrastructure.database.models.base import BaseModel


class ExpenseModel(BaseModel):
    __tablename__ = "expenses"

    group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("groups.id"),
        nullable=False,
        index=True,
    )
    paid_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    split_type: Mapped[str] = mapped_column(String(10), nullable=False)

    shares: Mapped[list[ExpenseShareModel]] = relationship(
        "ExpenseShareModel", back_populates="expense", lazy="selectin"
    )


class ExpenseShareModel(BaseModel):
    __tablename__ = "expense_shares"

    expense_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("expenses.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)

    expense: Mapped[ExpenseModel] = relationship("ExpenseModel", back_populates="shares")
