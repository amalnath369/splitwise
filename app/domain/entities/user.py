from __future__ import annotations
from dataclasses import dataclass, field
from app.domain.value_objects.email import Email
from app.domain.value_objects.entity_id import EntityID


@dataclass
class User:
    id: EntityID
    email: Email
    hashed_password: str
    is_deleted: bool = field(default=False)

    @classmethod
    def create(cls, email: Email, hashed_password: str) -> User:
        return cls(
            id=EntityID.generate(),
            email=email,
            hashed_password=hashed_password,
        )

    @property
    def is_active(self) -> bool:
        return not self.is_deleted

    def soft_delete(self) -> None:
        if self.is_deleted:
            raise ValueError("User is already deleted")
        self.is_deleted = True
