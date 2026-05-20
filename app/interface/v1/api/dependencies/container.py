from __future__ import annotations

from fastapi import Depends

from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.interface.v1.api.dependencies.dependency import get_uow

from app.application.auth.register import RegisterUseCase
from app.application.auth.login import LoginUseCase
from app.application.auth.logout import LogoutUseCase
from app.application.groups.create_group import CreateGroupUseCase
from app.application.groups.add_member import AddMemberUseCase
from app.application.groups.get_group import GetGroupUseCase
from app.application.expenses.create_expense import CreateExpenseUseCase
from app.application.expenses.list_expense import ListExpensesUseCase
from app.application.expenses.delete_expense import DeleteExpenseUseCase
from app.application.expenses.list_balances import GetBalancesUseCase
from app.application.expenses.get_settlements import GetSettlementsUseCase

from app.infrastructure.security.password import hash_password, verify_password
from app.infrastructure.security.token_service import create_token


def get_register_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> RegisterUseCase:
    return RegisterUseCase(uow=uow, hash_password=hash_password)


def get_login_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> LoginUseCase:
    return LoginUseCase(
        uow=uow,
        verify_password=verify_password,
        create_token=create_token,
    )


def get_logout_use_case() -> LogoutUseCase:
    return LogoutUseCase()


def get_create_group_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> CreateGroupUseCase:
    return CreateGroupUseCase(uow=uow)


def get_add_member_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> AddMemberUseCase:
    return AddMemberUseCase(uow=uow)


def get_group_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> GetGroupUseCase:
    return GetGroupUseCase(uow=uow)


def get_create_expense_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> CreateExpenseUseCase:
    return CreateExpenseUseCase(uow=uow)


def get_list_expenses_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> ListExpensesUseCase:
    return ListExpensesUseCase(uow=uow)


def get_delete_expense_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> DeleteExpenseUseCase:
    return DeleteExpenseUseCase(uow=uow)


def get_balances_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> GetBalancesUseCase:
    return GetBalancesUseCase(uow=uow)


def get_settlements_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> GetSettlementsUseCase:
    return GetSettlementsUseCase(uow=uow)
