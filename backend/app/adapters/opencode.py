"""OpenCode adapter for native dialogue"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import ExecutionAdapter
from ..models import Message
from ..config import settings


logger = logging.getLogger(__name__)


class OpenCodeAdapter(ExecutionAdapter):
    """
    Adapter for OpenCode server HTTP API
    Handles native dialogue sessions
    """

    def __init__(self):
        self.base_url = settings.opencode_base_url.rstrip("/")
        self.username = settings.opencode_username
        self.password = settings.opencode_password
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            auth = (self.username, self.password) if self.password else None
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                auth=auth,
                timeout=60.0
            )
        return self._client

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def create_session(
        self,
        resource_id: str,
        user_context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        """
        Create a new OpenCode session
        Returns the OpenCode session ID
        """
        client = await self._get_client()

        # Prepare session metadata
        metadata = {
            "portal_resource_id": resource_id,
            "portal_emp_no": user_context.get("emp_no", "unknown"),
            "portal_user_name": user_context.get("name", "unknown"),
            "created_at": datetime.utcnow().isoformat()
        }

        # Add skill-specific metadata if present
        if "skill_name" in config:
            metadata["skill_name"] = config["skill_name"]

        try:
            response = await client.post(
                "/session",
                json={
                    "metadata": metadata,
                    "workspace": config.get("workspace_id", "default")
                }
            )
            response.raise_for_status()

            data = response.json()
            session_id = data.get("id")

            logger.info(f"Created OpenCode session: {session_id}")
            return session_id

        except httpx.HTTPError as e:
            logger.error(f"Failed to create OpenCode session: {e}")
            raise

    async def send_message(
        self,
        session_id: str,
        message: str,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Send a message to OpenCode session
        Returns the assistant's response text
        """
        client = await self._get_client()

        # Prepare headers with trace ID
        headers = {}
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        try:
            # Send message via async prompt API
            response = await client.post(
                f"/session/{session_id}/prompt_async",
                json={"text": message},
                headers=headers
            )
            response.raise_for_status()

            data = response.json()
            assistant_message = data.get("text", "")

            logger.info(f"Sent message to session {session_id}, trace_id={trace_id}")
            return assistant_message

        except httpx.HTTPError as e:
            logger.error(f"Failed to send message to session {session_id}: {e}")
            raise

    async def get_messages(
        self,
        session_id: str,
        trace_id: Optional[str] = None
    ) -> List[Message]:
        """
        Get message history from OpenCode session
        """
        client = await self._get_client()

        # Prepare headers with trace ID
        headers = {}
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        try:
            response = await client.get(
                f"/session/{session_id}/message",
                headers=headers
            )
            response.raise_for_status()

            data = response.json()
            messages = []

            for msg in data.get("messages", []):
                messages.append(Message(
                    role=msg.get("role", "user"),
                    text=msg.get("text", ""),
                    timestamp=datetime.fromisoformat(msg["timestamp"]) if msg.get("timestamp") else None
                ))

            logger.info(f"Retrieved {len(messages)} messages from session {session_id}")
            return messages

        except httpx.HTTPError as e:
            logger.error(f"Failed to get messages from session {session_id}: {e}")
            raise

    async def close_session(
        self,
        session_id: str,
        trace_id: Optional[str] = None
    ) -> bool:
        """
        Close an OpenCode session
        """
        client = await self._get_client()

        # Prepare headers with trace ID
        headers = {}
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        try:
            response = await client.delete(
                f"/session/{session_id}",
                headers=headers
            )
            response.raise_for_status()

            logger.info(f"Closed OpenCode session: {session_id}")
            return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to close session {session_id}: {e}")
            return False
