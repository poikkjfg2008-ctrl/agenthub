"""OpenWork adapter for file-based skill management"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from ..config import settings


logger = logging.getLogger(__name__)


class OpenWorkAdapter:
    """
    Adapter for OpenWork server
    Handles skill file management and workspace operations
    """

    def __init__(self):
        self.base_url = settings.openwork_base_url.rstrip("/")
        self.token = settings.openwork_token
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0
            )
        return self._client

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def list_skills(
        self,
        workspace_id: str = "default",
        trace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List available skills in workspace
        """
        client = await self._get_client()

        # Prepare headers with trace ID
        headers = {}
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        try:
            response = await client.get(
                f"/workspace/{workspace_id}/skills",
                headers=headers
            )
            response.raise_for_status()

            data = response.json()
            skills = data.get("skills", [])

            logger.info(f"Listed {len(skills)} skills from workspace {workspace_id}")
            return skills

        except httpx.HTTPError as e:
            logger.error(f"Failed to list skills: {e}")
            return []

    async def get_skill_status(
        self,
        skill_name: str,
        workspace_id: str = "default",
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get skill installation status
        """
        client = await self._get_client()

        # Prepare headers with trace ID
        headers = {}
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        try:
            response = await client.get(
                f"/workspace/{workspace_id}/skills/{skill_name}",
                headers=headers
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Got skill status for: {skill_name}")
            return data

        except httpx.HTTPError as e:
            logger.error(f"Failed to get skill status for {skill_name}: {e}")
            return {"installed": False}

    async def reload_engine(
        self,
        workspace_id: str = "default",
        trace_id: Optional[str] = None
    ) -> bool:
        """
        Reload OpenWork engine to pick up new skills
        """
        client = await self._get_client()

        # Prepare headers with trace ID
        headers = {}
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        try:
            response = await client.post(
                f"/workspace/{workspace_id}/engine/reload",
                headers=headers
            )
            response.raise_for_status()

            logger.info(f"Reloaded engine for workspace {workspace_id}")
            return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to reload engine: {e}")
            return False
