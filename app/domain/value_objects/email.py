from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    value: str

    _PATTERN: re.Pattern = re.compile(
        r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    )
    MAX_LENGTH: int = 254

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("Email must be a string")

        normalized = self.value.strip().lower()

        if not normalized:
            raise ValueError("Email cannot be empty")

        if len(normalized) > self.MAX_LENGTH:
            raise ValueError(f"Email cannot exceed {self.MAX_LENGTH} characters")

        if not self._PATTERN.match(normalized):
            raise ValueError(f"Invalid email format: {self.value!r}")

        object.__setattr__(self, "value", normalized)

    @property
    def domain(self) -> str:
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        return self.value.split("@")[0]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"Email({self.value!r})"

    def __str__(self) -> str:
        return self.value
