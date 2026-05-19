from __future__ import annotations
from dataclasses import dataclass, field
from app.domain.value_objects.entity_id import EntityID


@dataclass
class GroupMember:
    group_id: EntityID
    user_id: EntityID


@dataclass
class Group:
    id: EntityID
    name: str
    created_by: EntityID
    description: str = ""
    member_ids: set[EntityID] = field(default_factory=set)

    @classmethod
    def create(cls, name: str, created_by: EntityID, description: str = "") -> Group:
        group = cls(
            id=EntityID.generate(),
            name=name,
            created_by=created_by,
            description=description,
            member_ids=set(),
        )
        group.add_member(created_by)
        return group

    def add_member(self, user_id: EntityID) -> None:
        if self.has_member(user_id):
            raise ValueError("User is already a member of the group")
        self.member_ids.add(user_id)

    def has_member(self, user_id: EntityID) -> bool:
        return user_id in self.member_ids
