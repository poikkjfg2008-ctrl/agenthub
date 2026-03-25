"""Authentication service - Mock SSO implementation"""

import uuid
import jwt
from datetime import datetime, timedelta
from typing import Optional
from ..models import UserCtx
from ..config import settings


class AuthService:
    """Authentication service for SSO resolution"""

    def __init__(self):
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm

    def create_mock_user(self, emp_no: str) -> UserCtx:
        """Create a mock user from employee number"""
        return UserCtx(
            emp_no=emp_no,
            name=f"User-{emp_no}",
            dept="demo",
            roles=["employee"],
            email=f"{emp_no}@company.com"
        )

    def generate_token(self, user: UserCtx) -> str:
        """Generate JWT token for user"""
        payload = {
            "emp_no": user.emp_no,
            "name": user.name,
            "dept": user.dept,
            "roles": user.roles,
            "email": user.email,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[UserCtx]:
        """Verify JWT token and return user context"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return UserCtx(**payload)
        except jwt.PyJWTError:
            return None

    def resolve_sso_user(self, code: str) -> Optional[UserCtx]:
        """
        Resolve user from SSO code (for future real SSO integration)
        Currently returns mock user
        """
        # Mock implementation - in production, call real SSO API
        return self.create_mock_user("E10001")


# Global auth service instance
auth_service = AuthService()
