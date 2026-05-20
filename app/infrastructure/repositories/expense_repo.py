from __future__ import annotations
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.expenses import Expense, ExpenseShare, SplitType
from app.domain.value_objects.entity_id import EntityID
from app.domain.value_objects.money import Money
from app.domain.repositories.expense_repo import AbstractExpenseRepository
from app.infrastructure.database.models.expenses import ExpenseModel, ExpenseShareModel


def _share_to_entity(model: ExpenseShareModel) -> ExpenseShare:
    return ExpenseShare(
        expense_id=EntityID(model.expense_id),
        user_id=EntityID(model.user_id),
        amount=Decimal(str(model.amount)),
        is_deleted=model.is_deleted,
    )


def _to_entity(model: ExpenseModel) -> Expense:
    expense = Expense(
        id=EntityID(model.id),
        group_id=EntityID(model.group_id),
        paid_by=EntityID(model.paid_by),
        description=model.description,
        amount=Money(amount=Decimal(str(model.amount))),
        split_type=SplitType(model.split_type),
        is_deleted=model.is_deleted,
        shares=[_share_to_entity(s) for s in model.shares if not s.is_deleted],
    )
    return expense


class ExpenseRepository(AbstractExpenseRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: EntityID) -> Expense | None:
        result = await self.session.execute(
            select(ExpenseModel)
            .where(ExpenseModel.id == id.value)
            .where(ExpenseModel.is_deleted == False)
        )
        model = result.scalars().first()
        return _to_entity(model) if model else None

    async def add(self, expense: Expense) -> None:
        model = ExpenseModel(
            id=expense.id.value,
            group_id=expense.group_id.value,
            paid_by=expense.paid_by.value,
            description=expense.description,
            amount=expense.amount.amount,
            split_type=expense.split_type.value,
            is_deleted=expense.is_deleted,
        )
        self.session.add(model)

        for share in expense.shares:
            self.session.add(ExpenseShareModel(
                expense_id=expense.id.value,
                user_id=share.user_id.value,
                amount=share.amount,
            ))

    async def update(self, expense: Expense) -> None:
        result = await self.session.execute(
            select(ExpenseModel).where(ExpenseModel.id == expense.id.value)
        )
        model = result.scalars().first()
        if model:
            model.is_deleted = expense.is_deleted

    async def soft_delete(self, id: EntityID) -> None:
        result = await self.session.execute(
            select(ExpenseModel).where(ExpenseModel.id == id.value)
        )
        model = result.scalars().first()
        if model:
            model.is_deleted = True

    async def list_by_group(
        self,
        group_id: EntityID,
        limit: int,
        offset: int,
    ) -> List[Expense]:
        result = await self.session.execute(
            select(ExpenseModel)
            .where(ExpenseModel.group_id == group_id.value)
            .where(ExpenseModel.is_deleted == False)
            .order_by(ExpenseModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def get_shares(self, expense_id: EntityID) -> List[ExpenseShare]:
        result = await self.session.execute(
            select(ExpenseShareModel)
            .where(ExpenseShareModel.expense_id == expense_id.value)
            .where(ExpenseShareModel.is_deleted == False)
        )
        return [_share_to_entity(m) for m in result.scalars().all()]
