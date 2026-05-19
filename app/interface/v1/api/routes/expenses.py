from __future__ import annotations
from decimal import Decimal
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends

from app.application.expenses.create_expense import CreateExpenseDTO, CreateExpenseUseCase
from app.application.expenses.list_expense import ListExpensesDTO, ListExpensesUseCase
from app.application.expenses.delete_expense import DeleteExpenseDTO, DeleteExpenseUseCase
from app.application.expenses.list_balances import GetBalancesDTO, GetBalancesUseCase
from app.application.expenses.get_settlements import GetSettlementsDTO, GetSettlementsUseCase
from app.interface.v1.schemas.expense import (
    CreateExpenseRequest,
    ExpenseResponse,
    ExpenseShareResponse,
    BalanceResponse,
    SettlementResponse,
)
from app.interface.v1.api.dependencies.dependency import get_current_user_id
from app.interface.v1.api.dependencies.pagination import PaginationParams
from app.interface.v1.api.dependencies.container import (
    get_create_expense_use_case,
    get_list_expenses_use_case,
    get_delete_expense_use_case,
    get_balances_use_case,
    get_settlements_use_case,
)

router = APIRouter(prefix="/groups", tags=["expenses"])


@router.post("/{group_id}/expenses", status_code=201, response_model=ExpenseResponse)
async def create_expense(
    group_id: UUID,
    body: CreateExpenseRequest,
    user_id: str = Depends(get_current_user_id),
    use_case: CreateExpenseUseCase = Depends(get_create_expense_use_case),
) -> ExpenseResponse:
    dto = CreateExpenseDTO(
        group_id=str(group_id),
        paid_by=str(body.paid_by),
        requester_id=user_id,
        amount=body.amount,
        description=body.description,
        split_type=body.split_type,
        split_between=[str(uid) for uid in body.split_between],
        exact_shares={str(k): v for k, v in body.exact_shares.items()} if body.exact_shares else None,
    )
    expense = await use_case.execute(dto)
    return ExpenseResponse(
        id=expense.id.value,
        group_id=expense.group_id.value,
        paid_by=expense.paid_by.value,
        description=expense.description,
        amount=expense.amount.amount,
        split_type=expense.split_type.value,
        shares=[ExpenseShareResponse(user_id=s.user_id.value, amount=s.amount) for s in expense.shares],
    )


@router.get("/{group_id}/expenses", response_model=List[ExpenseResponse])
async def list_expenses(
    group_id: UUID,
    user_id: str = Depends(get_current_user_id),
    pagination: PaginationParams = Depends(),
    use_case: ListExpensesUseCase = Depends(get_list_expenses_use_case),
) -> List[ExpenseResponse]:
    dto = ListExpensesDTO(
        group_id=str(group_id),
        requester_id=user_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    expenses = await use_case.execute(dto)
    return [
        ExpenseResponse(
            id=e.id.value,
            group_id=e.group_id.value,
            paid_by=e.paid_by.value,
            description=e.description,
            amount=e.amount.amount,
            split_type=e.split_type.value,
            shares=[ExpenseShareResponse(user_id=s.user_id.value, amount=s.amount) for s in e.shares],
        )
        for e in expenses
    ]


@router.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: UUID,
    user_id: str = Depends(get_current_user_id),
    use_case: DeleteExpenseUseCase = Depends(get_delete_expense_use_case),
) -> None:
    dto = DeleteExpenseDTO(expense_id=str(expense_id), requester_id=user_id)
    await use_case.execute(dto)


@router.get("/{group_id}/balances", response_model=List[BalanceResponse])
async def get_balances(
    group_id: UUID,
    user_id: str = Depends(get_current_user_id),
    use_case: GetBalancesUseCase = Depends(get_balances_use_case),
) -> List[BalanceResponse]:
    dto = GetBalancesDTO(group_id=str(group_id), requester_id=user_id)
    balances = await use_case.execute(dto)
    return [
        BalanceResponse(user_id=uid.value, balance=balance)
        for uid, balance in balances.items()
    ]


@router.get("/{group_id}/settlements", response_model=List[SettlementResponse])
async def get_settlements(
    group_id: UUID,
    user_id: str = Depends(get_current_user_id),
    use_case: GetSettlementsUseCase = Depends(get_settlements_use_case),
) -> List[SettlementResponse]:
    dto = GetSettlementsDTO(group_id=str(group_id), requester_id=user_id)
    settlements = await use_case.execute(dto)
    return [
        SettlementResponse(from_user=debtor.value, to_user=creditor.value, amount=amount)
        for debtor, creditor, amount in settlements
    ]
