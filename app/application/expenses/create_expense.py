from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from app.domain.entities.expenses import Expense, SplitType
from app.domain.value_objects.entity_id import EntityID
from app.domain.value_objects.money import Money
from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.domain.entities.split_service import calculate_equal_shares, calculate_exact_shares
from app.shared.exceptions import NotFoundError, ValidationError


@dataclass
class CreateExpenseDTO:
    group_id: str
    paid_by: str
    requester_id: str
    amount: Decimal
    split_type: str
    split_between: List[str]
    description: str = ""
    exact_shares: Optional[Dict[str, Decimal]] = None


class CreateExpenseUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: CreateExpenseDTO) -> Expense:
        group_id = EntityID.from_string(dto.group_id)
        paid_by = EntityID.from_string(dto.paid_by)
        requester_id = EntityID.from_string(dto.requester_id)
        amount = Money(amount=Decimal(str(dto.amount)))

        if not dto.split_between:
            raise ValidationError("split_between cannot be empty")

        split_between = [EntityID.from_string(uid) for uid in dto.split_between]

        if len(split_between) != len(set(str(uid) for uid in split_between)):
            raise ValidationError("Duplicate user IDs in split_between")

        try:
            split_type = SplitType(dto.split_type)
        except ValueError:
            raise ValidationError(f"Invalid split_type: {dto.split_type}")

        async with self.uow:
            group = await self.uow.groups.get_by_id(group_id)
            if not group or not group.has_member(requester_id):
                raise NotFoundError("Group not found")

            for uid in split_between:
                if not group.has_member(uid):
                    raise ValidationError(f"User {uid} is not a member of the group")

            expense = Expense.create(
                group_id=group_id,
                paid_by=paid_by,
                description=dto.description,
                amount=amount,
                split_type=split_type,
            )

            if split_type == SplitType.EQUAL:
                shares = calculate_equal_shares(expense.id, amount, split_between)
            else:
                if not dto.exact_shares:
                    raise ValidationError("exact_shares required for exact split")
                exact = {EntityID.from_string(k): v for k, v in dto.exact_shares.items()}
                shares = calculate_exact_shares(expense.id, amount, exact)

            for share in shares:
                expense.add_share(share)

            await self.uow.expenses.add(expense)
            await self.uow.commit()
            return expense
