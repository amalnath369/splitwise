from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.infrastructure.repositories.user_repo import UserRepository
from app.infrastructure.repositories.group_repo import GroupRepository
from app.infrastructure.repositories.expense_repo import ExpenseRepository


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self.users = UserRepository(self._session)
        self.groups = GroupRepository(self._session)
        self.expenses = ExpenseRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
