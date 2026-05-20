from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from app.domain.value_objects.entity_id import EntityID
from app.domain.value_objects.money import Money


class SplitType(str, Enum):
    EQUAL = "equal"
    EXACT = "exact"


@dataclass
class ExpenseShare:
    expense_id: EntityID
    user_id: EntityID
    amount: Decimal
    is_deleted: bool = False


@dataclass
class Expense:
    id: EntityID
    group_id: EntityID
    paid_by: EntityID
    description: str
    amount: Money
    split_type: SplitType
    shares: list[ExpenseShare] = field(default_factory=list)
    is_deleted: bool = False

    @classmethod
    def create(
        cls,
        group_id: EntityID,
        paid_by: EntityID,
        description: str,
        amount: Money,
        split_type: SplitType,
    ) -> Expense:
        return cls(
            id=EntityID.generate(),
            group_id=group_id,
            paid_by=paid_by,
            description=description,
            amount=amount,
            split_type=split_type,
        )

    def soft_delete(self) -> None:
        if self.is_deleted:
            raise ValueError("Expense is already deleted")
        self.is_deleted = True

    def add_share(self, share: ExpenseShare) -> None:
        self.shares.append(share)
