from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.domain.value_objects.entity_id import EntityID


T = TypeVar('T')


class AbstractBaseRepository(ABC, Generic[T]):

    @abstractmethod
    async def get_by_id(self, id: EntityID) -> T | None:
        pass

    @abstractmethod
    async def add(self, entity: T) -> None:
        pass

    @abstractmethod
    async def update(self, entity: T) -> None:
        pass

    @abstractmethod
    async def soft_delete(self, id: EntityID) -> None:
        pass