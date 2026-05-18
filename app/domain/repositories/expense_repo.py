from __future__ import annotations
from abc import abstractmethod
from typing import List

from app.domain.entities.expenses import Expense
from app.domain.value_objects.entity_id import EntityID
from app.domain.repositories.base import AbstractBaseRepository


class AbstractExpenseRepository(AbstractBaseRepository[Expense]):

    @abstractmethod
    async def list_by_group(self,group_id: EntityID,limit: int,offset: int,) -> List[Expense]:
        pass

    @abstractmethod
    async def get_shares(self, expense_id: EntityID) -> List[Expense]:
        pass
