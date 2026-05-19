from __future__ import annotations

from fastapi import APIRouter, Depends

from app.application.auth.login import LoginDTO, LoginUseCase
from app.application.auth.register import RegisterDTO, RegisterUseCase
from app.interface.v1.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RegisterResponse,
)
from app.interface.v1.api.dependencies.container import (
    get_register_use_case,
    get_login_use_case,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=RegisterResponse)
async def register(
    body: RegisterRequest,
    use_case: RegisterUseCase = Depends(get_register_use_case),
) -> RegisterResponse:
    dto = RegisterDTO(email=body.email, raw_password=body.password)
    user = await use_case.execute(dto)
    return RegisterResponse.model_validate(user, from_attributes=True)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> TokenResponse:
    dto = LoginDTO(email=body.email, raw_password=body.password)
    token = await use_case.execute(dto)
    return TokenResponse(access_token=token)
