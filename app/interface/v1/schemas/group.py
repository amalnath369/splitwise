from __future__ import annotations
from uuid import UUID
from typing import List

from pydantic import BaseModel


class CreateGroupRequest(BaseModel):
    name: str
    description: str = ""


class AddMemberRequest(BaseModel):
    email: str


class MemberResponse(BaseModel):
    user_id: UUID

    model_config = {"from_attributes": True}


class GroupResponse(BaseModel):
    id: UUID
    name: str
    description: str
    created_by: UUID
    members: List[MemberResponse]

    model_config = {"from_attributes": True}
