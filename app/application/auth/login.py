from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from app.domain.value_objects.email import Email
from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.shared.exceptions import UnauthorizedError


@dataclass
class LoginDTO:
    email: str
    raw_password: str


class LoginUseCase:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        verify_password: Callable[[str, str], bool],
        create_token: Callable[[str], str],
    ) -> None:
        self.uow = uow
        self.verify_password = verify_password
        self.create_token = create_token

    async def execute(self, dto: LoginDTO) -> str:
        email = Email(dto.email)

        async with self.uow:
            user = await self.uow.users.get_by_email(email)
            if not user or not user.is_active:
                raise UnauthorizedError("Invalid email or password")

            if not self.verify_password(dto.raw_password, user.hashed_password):
                raise UnauthorizedError("Invalid email or password")

            return self.create_token(str(user.id))
