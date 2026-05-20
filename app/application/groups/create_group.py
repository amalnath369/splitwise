from __future__ import annotations
from dataclasses import dataclass

from app.domain.value_objects.entity_id import EntityID
from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.domain.entities.groups import Group
from app.shared.exceptions import NotFoundError


@dataclass
class CreateGroupDTO:
    name: str
    created_by: str
    description: str = ""


class CreateGroupUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: CreateGroupDTO) -> Group:
        created_by = EntityID.from_string(dto.created_by)

        async with self.uow:
            owner = await self.uow.users.get_by_id(created_by)
            if not owner or not owner.is_active:
                raise NotFoundError("User does not exist or is inactive")

            group = Group.create(name=dto.name, created_by=created_by, description=dto.description)
            await self.uow.groups.add(group)
            await self.uow.commit()
            return group
