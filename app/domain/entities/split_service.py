from __future__ import annotations
from decimal import Decimal, ROUND_DOWN
from typing import List, Dict, Tuple

from app.domain.entities.expenses import Expense, ExpenseShare, SplitType
from app.domain.value_objects.entity_id import EntityID
from app.domain.value_objects.money import Money


def calculate_equal_shares(
    expense_id: EntityID,
    amount: Money,
    user_ids: List[EntityID],
) -> List[ExpenseShare]:
    """
    Split amount equally among user_ids.
    Base share is ROUND_DOWN; first `remainder` users get +0.01.
    This is deterministic — same input always yields same distribution.
    """
    n = len(user_ids)
    cent = Decimal("0.01")
    base = (amount.amount / Decimal(n)).quantize(cent, rounding=ROUND_DOWN)
    remainder = int((amount.amount - base * Decimal(n)) / cent)

    shares = []
    for i, user_id in enumerate(user_ids):
        share_amount = base + cent if i < remainder else base
        shares.append(
            ExpenseShare(
                expense_id=expense_id,
                user_id=user_id,
                amount=share_amount,
            )
        )
    return shares


def calculate_exact_shares(
    expense_id: EntityID,
    amount: Money,
    user_shares: Dict[EntityID, Decimal],
) -> List[ExpenseShare]:
    """
    Validate that provided exact shares sum to total, then build ExpenseShare list.
    Raises ValueError if shares do not sum to amount.
    """
    total = sum(user_shares.values(), Decimal("0"))
    if total != amount.amount:
        raise ValueError(
            f"Exact shares sum to {total} but expense amount is {amount.amount}"
        )

    return [
        ExpenseShare(expense_id=expense_id, user_id=user_id, amount=share)
        for user_id, share in user_shares.items()
    ]


def compute_balances(expenses: List[Expense]) -> Dict[EntityID, Decimal]:
    """
    Compute net balance per user across all expenses.
    Positive = others owe them. Negative = they owe others.
    Self-inclusion is handled naturally:
      payer gets +full_amount, their own share subtracts from that.
    Only non-deleted expenses are considered.
    """
    balances: Dict[EntityID, Decimal] = {}

    for expense in expenses:
        if expense.is_deleted:
            continue

        balances[expense.paid_by] = (
            balances.get(expense.paid_by, Decimal("0")) + expense.amount.amount
        )

        for share in expense.shares:
            balances[share.user_id] = (
                balances.get(share.user_id, Decimal("0")) - share.amount
            )

    return balances


def compute_settlements(
    balances: Dict[EntityID, Decimal],
) -> List[Tuple[EntityID, EntityID, Decimal]]:
    """
    Greedy algorithm to minimize number of transactions.
    Returns list of (debtor, creditor, amount) tuples.
    """
    creditors: List[List] = [
        [uid, bal] for uid, bal in balances.items() if bal > Decimal("0")
    ]
    debtors: List[List] = [
        [uid, -bal] for uid, bal in balances.items() if bal < Decimal("0")
    ]

    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    settlements = []

    while creditors and debtors:
        debtor_id, debt = debtors[0]
        creditor_id, credit = creditors[0]

        amount = min(debt, credit)
        settlements.append((debtor_id, creditor_id, amount))

        debtors[0][1] -= amount
        creditors[0][1] -= amount

        if debtors[0][1] == Decimal("0"):
            debtors.pop(0)
        if creditors[0][1] == Decimal("0"):
            creditors.pop(0)

    return settlements
