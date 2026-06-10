from fastapi import APIRouter, HTTPException, status

from src.application.exceptions import (
    EmailAlreadyTakenError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotFoundError,
)
from src.presentation.api.dependencies import (
    CurrentUserIdDep,
    GetUserDep,
    LoginUserDep,
    RefreshTokenDep,
    RegisterUserDep,
)
from src.presentation.api.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, usecase: RegisterUserDep) -> RegisterResponse:
    try:
        user_id = await usecase.execute(
            name=body.name, email=body.email, password=body.password
        )
    except EmailAlreadyTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already taken",
        )
    return RegisterResponse(user_id=user_id)


@router.post("/login")
async def login(body: LoginRequest, usecase: LoginUserDep) -> TokenResponse:
    try:
        pair = await usecase.execute(email=body.email, password=body.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return TokenResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
    )


@router.post("/refresh")
async def refresh(body: RefreshRequest, usecase: RefreshTokenDep) -> TokenResponse:
    try:
        pair = await usecase.execute(body.refresh_token)
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return TokenResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
    )


@router.get("/users/me")
async def get_me(
    current_user_id: CurrentUserIdDep, usecase: GetUserDep
) -> UserResponse:
    try:
        user = await usecase.execute(current_user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse(user_id=user.id, name=user.name, email=user.email)
