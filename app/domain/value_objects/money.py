from __future__ import annotations
from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "INR"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError("amount must be a Decimal")
        if self.amount <= Decimal("0"):
            raise ValueError("amount must be positive")

    def split(self, n: int) -> List["Money"]:
        """
        Split into n shares. Base share is ROUND_DOWN; remainder cents
        distributed one each to the first `remainder` recipients.
        This is deterministic: same inputs always yield same distribution.
        """
        if n <= 0:
            raise ValueError("n must be a positive integer")

        cent = Decimal("0.01")
        base = (self.amount / Decimal(n)).quantize(cent, rounding=ROUND_DOWN)
        remainder = int((self.amount - base * Decimal(n)) / cent)

        shares: List[Money] = []
        for i in range(n):
            share = base + cent if i < remainder else base
            shares.append(Money(amount=share, currency=self.currency))

        return shares

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __repr__(self) -> str:
        return f"Money({self.amount}, {self.currency})"

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Currency mismatch: {self.currency} vs {other.currency}"
            )
