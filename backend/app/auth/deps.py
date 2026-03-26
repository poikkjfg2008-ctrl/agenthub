"""Authentication dependencies for FastAPI routes"""

from typing import Annotated
from fastapi import Cookie, Depends, HTTPException, status
from ..config import settings
from .service import auth_service
from ..models import UserCtx


async def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None
) -> UserCtx:
    """
    Get current user from JWT token in cookie
    Raises HTTPException if not authenticated
    """
    if not access_token:
        if settings.auth_mock_fallback_enabled:
            return auth_service.create_mock_user("E10001")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user = auth_service.verify_token(access_token)
    if not user:
        if settings.auth_mock_fallback_enabled:
            return auth_service.create_mock_user("E10001")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return user


async def get_optional_user(
    access_token: Annotated[str | None, Cookie()] = None
) -> UserCtx | None:
    """
    Get current user from JWT token if available
    Returns None if not authenticated
    """
    if not access_token:
        if settings.auth_mock_fallback_enabled:
            return auth_service.create_mock_user("E10001")
        return None

    user = auth_service.verify_token(access_token)
    if not user:
        if settings.auth_mock_fallback_enabled:
            return auth_service.create_mock_user("E10001")
        return None

    return user


# Type aliases for dependency injection
CurrentUser = Annotated[UserCtx, Depends(get_current_user)]
OptionalUser = Annotated[UserCtx | None, Depends(get_optional_user)]
