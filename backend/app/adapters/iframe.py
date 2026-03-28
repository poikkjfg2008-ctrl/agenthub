"""Iframe adapter for direct iframe embedding"""

import secrets
import logging
from typing import Dict, Any
from datetime import datetime

from ..models import LaunchRecord, IframeConfig, UserCtx, Resource


logger = logging.getLogger(__name__)


class IframeAdapter:
    """
    Adapter for direct iframe embedding
    Handles iframe launch token generation and embed configuration
    """

    def __init__(self):
        pass

    def generate_launch_token(self) -> str:
        """
        Generate a secure launch token
        """
        return secrets.token_urlsafe(32)

    def create_launch_record(
        self,
        resource: Resource,
        user: UserCtx
    ) -> LaunchRecord:
        """
        Create a launch record for iframe embedding
        """
        import uuid

        launch_record = LaunchRecord(
            launch_id=str(uuid.uuid4()),
            resource_id=resource.id,
            user_emp_no=user.emp_no,
            launch_token=self.generate_launch_token(),
            user_context={
                "emp_no": user.emp_no,
                "name": user.name,
                "dept": user.dept,
                "email": user.email
            }
        )

        logger.info(f"Created iframe launch record: {launch_record.launch_id} for resource: {resource.id}")
        return launch_record

    def get_iframe_config(
        self,
        launch_record: LaunchRecord,
        resource: Resource
    ) -> IframeConfig:
        """
        Get iframe embed configuration
        """
        # Get iframe_url from resource config
        iframe_url = resource.config.iframe_url or ""
        
        config = IframeConfig(
            iframe_url=iframe_url,
            user_context=launch_record.user_context
        )

        logger.info(f"Generated iframe config for launch: {launch_record.launch_id}")
        return config

    def validate_launch_token(self, launch_token: str) -> bool:
        """
        Validate a launch token
        """
        # Basic token validation - in production, verify against stored launch records
        return len(launch_token) >= 32
