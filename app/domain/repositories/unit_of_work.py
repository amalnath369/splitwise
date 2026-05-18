from __future__ import annotations
from abc import ABC, abstractmethod

from app.domain.repositories.user_repo import AbstractUserRepository
from app.domain.repositories.group_repo import AbstractGroupRepository
from app.domain.repositories.expense_repo import AbstractExpenseRepository


class AbstractUnitOfWork(ABC):

    users: AbstractUserRepository
    groups: AbstractGroupRepository
    expenses: AbstractExpenseRepository

    @abstractmethod
    async def __aenter__(self) -> AbstractUnitOfWork:
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass