from __future__ import annotations
from dataclasses import dataclass

from app.domain.entities.groups import Group
from app.domain.value_objects.entity_id import EntityID
from app.domain.value_objects.email import Email
from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.shared.exceptions import NotFoundError, ForbiddenError


@dataclass
class AddMemberDTO:
    group_id: str
    requester_id: str
    email: str


class AddMemberUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: AddMemberDTO) -> Group:
        group_id = EntityID.from_string(dto.group_id)
        requester_id = EntityID.from_string(dto.requester_id)
        email = Email(dto.email)

        async with self.uow:
            group = await self.uow.groups.get_by_id(group_id)
            if not group or not group.has_member(requester_id):
                raise NotFoundError("Group not found")

            user = await self.uow.users.get_by_email(email)
            if not user or not user.is_active:
                raise NotFoundError("User not found")

            group.add_member(user.id)
            await self.uow.groups.update(group)
            await self.uow.commit()
            return group
