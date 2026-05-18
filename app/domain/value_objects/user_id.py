from __future__ import annotations
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class UserID:
    value: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, uuid.UUID):
            raise TypeError("UserID value must be a UUID")

    @classmethod
    def generate(cls) -> UserID:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, value: str) -> UserID:
        try:
            return cls(value=uuid.UUID(value))
        except ValueError:
            raise ValueError(f"Invalid UUID string: {value!r}")

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"UserID({self.value!r})"

    def __hash__(self) -> int:
        return hash(self.value)
