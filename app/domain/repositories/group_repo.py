from __future__ import annotations
from abc import abstractmethod
from typing import List

from app.domain.entities.groups import Group
from app.domain.value_objects.entity_id import EntityID
from app.domain.repositories.base import AbstractBaseRepository


class AbstractGroupRepository(AbstractBaseRepository[Group]):

    @abstractmethod
    async def get_members(self, group_id: EntityID) -> List[EntityID]:
        pass
