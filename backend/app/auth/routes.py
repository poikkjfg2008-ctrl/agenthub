"""Authentication routes - Mock SSO endpoints"""

from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from typing import Annotated
from pydantic import BaseModel

from .service import auth_service
from .deps import CurrentUser
from ..models import UserCtx


router = APIRouter(prefix="/api/auth", tags=["authentication"])


class MockLoginRequest(BaseModel):
    """Mock login request"""
    emp_no: str


class UserInfoResponse(BaseModel):
    """User info response"""
    emp_no: str
    name: str
    dept: str
    roles: list[str]
    email: str | None


@router.get("/mock-login")
async def mock_login(emp_no: str, response: Response):
    """
    Mock SSO login endpoint
    In production, replace with real SSO flow
    """
    if not emp_no:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="emp_no parameter is required"
        )

    # Create mock user
    user = auth_service.create_mock_user(emp_no)

    # Generate JWT token
    token = auth_service.generate_token(user)

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400  # 24 hours
    )

    # Return JSON response with redirect info
    return {
        "message": "Login successful",
        "redirect": "/",
        "user": {
            "emp_no": user.emp_no,
            "name": user.name,
            "dept": user.dept
        }
    }


@router.get("/callback")
async def sso_callback(code: str, response: Response):
    """
    Real SSO callback endpoint (for future implementation)
    Currently redirects to mock login
    """
    # TODO: Implement real SSO callback
    # For now, redirect to mock login
    return RedirectResponse(url="/api/auth/mock-login?emp_no=E10001")


@router.get("/me", response_model=UserInfoResponse)
async def get_me(user: CurrentUser) -> UserInfoResponse:
    """Get current user information"""
    return UserInfoResponse(
        emp_no=user.emp_no,
        name=user.name,
        dept=user.dept,
        roles=user.roles,
        email=user.email
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing cookie"""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}
