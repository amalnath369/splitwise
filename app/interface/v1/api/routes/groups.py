from __future__ import annotations
from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.groups.create_group import CreateGroupDTO, CreateGroupUseCase
from app.application.groups.add_member import AddMemberDTO, AddMemberUseCase
from app.application.groups.get_group import GetGroupDTO, GetGroupUseCase
from app.interface.v1.schemas.group import (
    CreateGroupRequest,
    AddMemberRequest,
    GroupResponse,
    MemberResponse,
)
from app.interface.v1.api.dependencies.dependency import get_current_user_id
from app.interface.v1.api.dependencies.container import (
    get_create_group_use_case,
    get_add_member_use_case,
    get_group_use_case,
)

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", status_code=201, response_model=GroupResponse)
async def create_group(
    body: CreateGroupRequest,
    user_id: str = Depends(get_current_user_id),
    use_case: CreateGroupUseCase = Depends(get_create_group_use_case),
) -> GroupResponse:
    dto = CreateGroupDTO(name=body.name, description=body.description, created_by=user_id)
    group = await use_case.execute(dto)
    return GroupResponse(
        id=group.id.value,
        name=group.name,
        description=group.description,
        created_by=group.created_by.value,
        members=[MemberResponse(user_id=uid.value) for uid in group.member_ids],
    )


@router.post("/{group_id}/members", status_code=201, response_model=GroupResponse)
async def add_member(
    group_id: UUID,
    body: AddMemberRequest,
    user_id: str = Depends(get_current_user_id),
    use_case: AddMemberUseCase = Depends(get_add_member_use_case),
) -> GroupResponse:
    dto = AddMemberDTO(
        group_id=str(group_id),
        requester_id=user_id,
        email=body.email,
    )
    group = await use_case.execute(dto)
    return GroupResponse(
        id=group.id.value,
        name=group.name,
        description=group.description,
        created_by=group.created_by.value,
        members=[MemberResponse(user_id=uid.value) for uid in group.member_ids],
    )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: UUID,
    user_id: str = Depends(get_current_user_id),
    use_case: GetGroupUseCase = Depends(get_group_use_case),
) -> GroupResponse:
    dto = GetGroupDTO(group_id=str(group_id), requester_id=user_id)
    group = await use_case.execute(dto)
    return GroupResponse(
        id=group.id.value,
        name=group.name,
        description=group.description,
        created_by=group.created_by.value,
        members=[MemberResponse(user_id=uid.value) for uid in group.member_ids],
    )
