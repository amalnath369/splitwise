from __future__ import annotations
from abc import abstractmethod
from typing import Optional

from app.domain.value_objects.email import Email
from app.domain.entities.user import User
from app.domain.repositories.base import AbstractBaseRepository


class AbstractUserRepository(AbstractBaseRepository[User]):

    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        pass