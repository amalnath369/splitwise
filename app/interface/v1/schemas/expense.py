from __future__ import annotations
from decimal import Decimal
from uuid import UUID
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator


class CreateExpenseRequest(BaseModel):
    paid_by: UUID
    amount: Decimal
    description: str = ""
    split_type: str
    split_between: List[UUID]
    exact_shares: Optional[Dict[UUID, Decimal]] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= Decimal("0"):
            raise ValueError("Amount must be positive")
        return v

    @field_validator("split_between")
    @classmethod
    def split_between_no_duplicates(cls, v: List[UUID]) -> List[UUID]:
        if not v:
            raise ValueError("split_between cannot be empty")
        if len(v) != len(set(v)):
            raise ValueError("Duplicate user IDs in split_between")
        return v

    @field_validator("split_type")
    @classmethod
    def split_type_valid(cls, v: str) -> str:
        if v not in ("equal", "exact"):
            raise ValueError("split_type must be 'equal' or 'exact'")
        return v

    @model_validator(mode="after")
    def exact_shares_required_when_exact(self) -> CreateExpenseRequest:
        if self.split_type == "exact" and not self.exact_shares:
            raise ValueError("exact_shares required when split_type is 'exact'")
        return self


class ExpenseShareResponse(BaseModel):
    user_id: UUID
    amount: Decimal


class ExpenseResponse(BaseModel):
    id: UUID
    group_id: UUID
    paid_by: UUID
    description: str
    amount: Decimal
    split_type: str
    shares: List[ExpenseShareResponse]

    model_config = {"from_attributes": True}


class BalanceResponse(BaseModel):
    user_id: UUID
    balance: Decimal


class SettlementResponse(BaseModel):
    from_user: UUID
    to_user: UUID
    amount: Decimal
