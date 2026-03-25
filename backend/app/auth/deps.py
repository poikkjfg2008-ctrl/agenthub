"""Authentication dependencies for FastAPI routes"""

from typing import Annotated
from fastapi import Cookie, HTTPException, status, Depends
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no access token"
        )

    user = auth_service.verify_token(access_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
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
        return None

    return auth_service.verify_token(access_token)


# Type aliases for dependency injection
CurrentUser = Annotated[UserCtx, Depends(get_current_user)]
OptionalUser = Annotated[UserCtx | None, Depends(get_optional_user)]
