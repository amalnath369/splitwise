from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.models.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
