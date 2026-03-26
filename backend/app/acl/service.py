"""Access Control List service"""

from typing import List, Optional, Dict, Any
from ..models import Resource, UserCtx


class ACLService:
    """Access control service for resource authorization"""

    def __init__(self):
        # Default access rules - in production, load from database or config
        self.default_roles = ["employee", "admin", "manager"]

    def check_resource_access(
        self,
        resource: Resource,
        user: UserCtx
    ) -> bool:
        """
        Check if user has access to a resource
        """
        # Check if resource is enabled
        if not resource.enabled:
            return False

        # If no ACL defined, allow access (default allow)
        if not resource.acl:
            return True

        # Check ACL rules
        acl = resource.acl

        # Check role-based access
        if "allowed_roles" in acl:
            if not any(role in acl["allowed_roles"] for role in user.roles):
                return False

        # Check department-based access
        if "allowed_depts" in acl:
            if user.dept not in acl["allowed_depts"]:
                return False

        # Check user whitelist
        if "allowed_users" in acl:
            if user.emp_no not in acl["allowed_users"]:
                return False

        # Check user blacklist
        if "denied_users" in acl:
            if user.emp_no in acl["denied_users"]:
                return False

        return True

    def filter_accessible_resources(
        self,
        resources: List[Resource],
        user: UserCtx
    ) -> List[Resource]:
        """
        Filter resources that user has access to
        """
        return [
            resource for resource in resources
            if self.check_resource_access(resource, user)
        ]


# Global ACL service instance
acl_service = ACLService()
