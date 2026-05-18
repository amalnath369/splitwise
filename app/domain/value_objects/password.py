from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Password:
    value: str

    MIN_LENGTH: int = 8
    MAX_LENGTH: int = 128

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("Password must be a string")
        self._validate_strength(self.value)

    @classmethod
    def _validate_strength(cls, raw: str) -> None:
        errors = []

        if len(raw) < cls.MIN_LENGTH:
            errors.append(f"at least {cls.MIN_LENGTH} characters")

        if len(raw) > cls.MAX_LENGTH:
            errors.append(f"no more than {cls.MAX_LENGTH} characters")

        if not re.search(r"[A-Z]", raw):
            errors.append("at least one uppercase letter")

        if not re.search(r"[a-z]", raw):
            errors.append("at least one lowercase letter")

        if not re.search(r"\d", raw):
            errors.append("at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", raw):
            errors.append("at least one special character")

        if errors:
            raise ValueError("Password must contain: " + ", ".join(errors))

    def __repr__(self) -> str:
        return "Password(***)"

    def __str__(self) -> str:
        return "***"

    def __hash__(self) -> int:
        return hash(self.value)
