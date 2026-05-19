from __future__ import annotations
from dataclasses import dataclass
from typing import List

from app.domain.entities.expenses import Expense
from app.domain.value_objects.entity_id import EntityID
from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.shared.exceptions import NotFoundError


@dataclass
class ListExpensesDTO:
    group_id: str
    requester_id: str
    limit: int = 20
    offset: int = 0


class ListExpensesUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: ListExpensesDTO) -> List[Expense]:
        group_id = EntityID.from_string(dto.group_id)
        requester_id = EntityID.from_string(dto.requester_id)

        async with self.uow:
            group = await self.uow.groups.get_by_id(group_id)
            if not group or not group.has_member(requester_id):
                raise NotFoundError("Group not found")

            return await self.uow.expenses.list_by_group(
                group_id=group_id,
                limit=dto.limit,
                offset=dto.offset,
            )
