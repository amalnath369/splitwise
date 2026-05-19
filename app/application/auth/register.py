from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.shared.exceptions import ConflictError


@dataclass
class RegisterDTO:
    email: str
    raw_password: str


class RegisterUseCase:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        hash_password: Callable[[str], str],
    ) -> None:
        self.uow = uow
        self.hash_password = hash_password

    async def execute(self, dto: RegisterDTO) -> User:
        email = Email(dto.email)
        Password(dto.raw_password)  # validates strength, raises ValueError if weak

        async with self.uow:
            existing = await self.uow.users.get_by_email(email)
            if existing:
                raise ConflictError("Email is already registered")

            hashed = self.hash_password(dto.raw_password)
            user = User.create(email=email, hashed_password=hashed)
            await self.uow.users.add(user)
            await self.uow.commit()
            return user
