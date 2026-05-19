from __future__ import annotations
from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.unit_of_work import AbstractUnitOfWork
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.database.session import get_session
from app.infrastructure.security.token_service import verify_token

_bearer = HTTPBearer()


async def get_uow(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[AbstractUnitOfWork, None]:
    yield SqlAlchemyUnitOfWork(session)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    token = credentials.credentials
    return verify_token(token)
