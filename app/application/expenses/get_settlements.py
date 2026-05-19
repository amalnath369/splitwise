from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Tuple

from app.domain.value_objects.entity_id import EntityID
from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.domain.entities.split_service import compute_balances, compute_settlements
from app.shared.exceptions import NotFoundError


@dataclass
class GetSettlementsDTO:
    group_id: str
    requester_id: str


class GetSettlementsUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, dto: GetSettlementsDTO
    ) -> List[Tuple[EntityID, EntityID, Decimal]]:
        group_id = EntityID.from_string(dto.group_id)
        requester_id = EntityID.from_string(dto.requester_id)

        async with self.uow:
            group = await self.uow.groups.get_by_id(group_id)
            if not group or not group.has_member(requester_id):
                raise NotFoundError("Group not found")

            expenses = await self.uow.expenses.list_by_group(
                group_id=group_id,
                limit=10_000,
                offset=0,
            )

            balances = compute_balances(expenses)
            return compute_settlements(balances)
