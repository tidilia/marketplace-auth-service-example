from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import (
    DeleteUserPort,
    GetUserPort,
    LoginUserPort,
    RefreshTokenPort,
    RegisterUserPort,
)
from src.application.usecases.delete_user import DeleteUser
from src.application.usecases.get_user import GetUser
from src.application.usecases.login_user import LoginUser
from src.application.usecases.refresh_token import RefreshToken
from src.application.usecases.register_user import RegisterUser
from src.infrastructure.persistence.uow import SQLAlchemyUnitOfWork
from src.settings import Settings

_settings: Settings | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def setup(
    settings: Settings, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    global _settings, _session_factory
    _settings = settings
    _session_factory = session_factory


def get_settings() -> Settings:
    assert _settings is not None
    return _settings


def get_uow() -> UnitOfWork:
    assert _session_factory is not None
    return SQLAlchemyUnitOfWork(_session_factory)


def get_register_user(uow: "UowDep") -> RegisterUserPort:
    return RegisterUser(uow)


def get_login_user(uow: "UowDep", settings: "SettingsDep") -> LoginUserPort:
    return LoginUser(
        uow=uow,
        jwt_secret=settings.jwt_secret,
        jwt_algorithm=settings.jwt_algorithm,
        jwt_expire_hours=settings.jwt_expire_hours,
        jwt_refresh_expire_days=settings.jwt_refresh_expire_days,
    )


def get_refresh_token(uow: "UowDep", settings: "SettingsDep") -> RefreshTokenPort:
    return RefreshToken(
        uow=uow,
        jwt_secret=settings.jwt_secret,
        jwt_algorithm=settings.jwt_algorithm,
        jwt_expire_hours=settings.jwt_expire_hours,
        jwt_refresh_expire_days=settings.jwt_refresh_expire_days,
    )


def get_get_user(uow: "UowDep") -> GetUserPort:
    return GetUser(uow)


def get_delete_user(uow: "UowDep") -> DeleteUserPort:
    return DeleteUser(uow)


bearer_scheme = HTTPBearer()


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    settings: "SettingsDep",
) -> int:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload["user_id"]


SettingsDep = Annotated[Settings, Depends(get_settings)]
UowDep = Annotated[UnitOfWork, Depends(get_uow)]
CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]
RegisterUserDep = Annotated[RegisterUserPort, Depends(get_register_user)]
LoginUserDep = Annotated[LoginUserPort, Depends(get_login_user)]
RefreshTokenDep = Annotated[RefreshTokenPort, Depends(get_refresh_token)]
GetUserDep = Annotated[GetUserPort, Depends(get_get_user)]
DeleteUserDep = Annotated[DeleteUserPort, Depends(get_delete_user)]
