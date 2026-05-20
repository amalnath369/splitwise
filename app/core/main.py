from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.shared.exceptions import (
    AppError,
    NotFoundError,
    ForbiddenError,
    ConflictError,
    UnauthorizedError,
    ValidationError,
)
from app.infrastructure.database.models import Base
from app.infrastructure.database.session import engine
from app.interface.v1.api.routes.auth import router as auth_router
from app.interface.v1.api.routes.groups import router as groups_router
from app.interface.v1.api.routes.expenses import router as expenses_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)


# --- Exception handlers ---

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": exc.message})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": exc.message})


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.message})


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": exc.message})


# --- Routers ---

app.include_router(auth_router, prefix="/api/v1")
app.include_router(groups_router, prefix="/api/v1")
app.include_router(expenses_router, prefix="/api/v1")
