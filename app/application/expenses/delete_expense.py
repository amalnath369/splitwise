from __future__ import annotations
from dataclasses import dataclass

from app.domain.value_objects.entity_id import EntityID
from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.shared.exceptions import NotFoundError, ForbiddenError


@dataclass
class DeleteExpenseDTO:
    expense_id: str
    requester_id: str


class DeleteExpenseUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: DeleteExpenseDTO) -> None:
        expense_id = EntityID.from_string(dto.expense_id)
        requester_id = EntityID.from_string(dto.requester_id)

        async with self.uow:
            expense = await self.uow.expenses.get_by_id(expense_id)
            if not expense:
                raise NotFoundError("Expense not found")

            group = await self.uow.groups.get_by_id(expense.group_id)
            if not group or not group.has_member(requester_id):
                raise NotFoundError("Expense not found")

            if expense.paid_by != requester_id:
                raise ForbiddenError("Only the payer can delete this expense")

            expense.soft_delete()
            await self.uow.expenses.update(expense)
            await self.uow.commit()
