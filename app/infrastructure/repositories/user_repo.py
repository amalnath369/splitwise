from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.entity_id import EntityID
from app.domain.repositories.user_repo import AbstractUserRepository
from app.infrastructure.database.models.users import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=EntityID(model.id),
        email=Email(model.email),
        hashed_password=model.hashed_password,
        is_deleted=model.is_deleted,
    )


class UserRepository(AbstractUserRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: EntityID) -> User | None:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.id == id.value)
            .where(UserModel.is_deleted == False)
        )
        model = result.scalars().first()
        return _to_entity(model) if model else None

    async def get_by_email(self, email: Email) -> User | None:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.email == email.value)
            .where(UserModel.is_deleted == False)
        )
        model = result.scalars().first()
        return _to_entity(model) if model else None

    async def add(self, user: User) -> None:
        model = UserModel(
            id=user.id.value,
            email=user.email.value,
            hashed_password=user.hashed_password,
            is_deleted=user.is_deleted,
        )
        self.session.add(model)

    async def update(self, user: User) -> None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id.value)
        )
        model = result.scalars().first()
        if model:
            model.hashed_password = user.hashed_password
            model.is_deleted = user.is_deleted

    async def soft_delete(self, id: EntityID) -> None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == id.value)
        )
        model = result.scalars().first()
        if model:
            model.is_deleted = True
