from __future__ import annotations
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.groups import Group
from app.domain.value_objects.entity_id import EntityID
from app.domain.repositories.group_repo import AbstractGroupRepository
from app.infrastructure.database.models.groups import GroupModel, GroupMemberModel


def _to_entity(model: GroupModel) -> Group:
    return Group(
        id=EntityID(model.id),
        name=model.name,
        description=model.description,
        created_by=EntityID(model.created_by),
        member_ids={EntityID(m.user_id) for m in model.members if not m.is_deleted},
    )


class GroupRepository(AbstractGroupRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: EntityID) -> Group | None:
        result = await self.session.execute(
            select(GroupModel)
            .where(GroupModel.id == id.value)
            .where(GroupModel.is_deleted == False)
        )
        model = result.scalars().first()
        return _to_entity(model) if model else None

    async def add(self, group: Group) -> None:
        model = GroupModel(
            id=group.id.value,
            name=group.name,
            description=group.description,
            created_by=group.created_by.value,
        )
        self.session.add(model)

        for user_id in group.member_ids:
            self.session.add(GroupMemberModel(
                group_id=group.id.value,
                user_id=user_id.value,
            ))

    async def update(self, group: Group) -> None:
        result = await self.session.execute(
            select(GroupModel).where(GroupModel.id == group.id.value)
        )
        model = result.scalars().first()
        if not model:
            return

        model.name = group.name
        model.description = group.description

        existing = await self.session.execute(
            select(GroupMemberModel)
            .where(GroupMemberModel.group_id == group.id.value)
            .where(GroupMemberModel.is_deleted == False)
        )
        existing_ids = {EntityID(m.user_id) for m in existing.scalars().all()}
        new_ids = group.member_ids - existing_ids

        for user_id in new_ids:
            self.session.add(GroupMemberModel(
                group_id=group.id.value,
                user_id=user_id.value,
            ))

    async def get_members(self, group_id: EntityID) -> List[EntityID]:
        result = await self.session.execute(
            select(GroupMemberModel)
            .where(GroupMemberModel.group_id == group_id.value)
            .where(GroupMemberModel.is_deleted == False)
        )
        return [EntityID(m.user_id) for m in result.scalars().all()]

    async def soft_delete(self, id: EntityID) -> None:
        result = await self.session.execute(
            select(GroupModel).where(GroupModel.id == id.value)
        )
        model = result.scalars().first()
        if model:
            model.is_deleted = True
