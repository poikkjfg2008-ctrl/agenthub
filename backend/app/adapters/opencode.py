"""OpenCode adapter for native dialogue"""

import httpx
import logging
import asyncio
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
        self._client_lock = asyncio.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with event loop safety"""
        current_loop = asyncio.get_running_loop()
        
        async with self._client_lock:
            # Check if we need to recreate client (new loop or no client)
            if self._client is None or self._loop != current_loop:
                # Close old client if exists
                if self._client is not None:
                    try:
                        await self._client.aclose()
                    except Exception as e:
                        logger.warning(f"Error closing old client: {e}")
                
                # Only use auth if both username and password are provided
                auth = (self.username, self.password) if self.username and self.password else None
                self._client = httpx.AsyncClient(
                    base_url=self.base_url,
                    auth=auth,
                    timeout=60.0
                )
                self._loop = current_loop
                logger.debug(f"Created new httpx client for loop {id(current_loop)}")
            
            return self._client

    async def close(self):
        """Close HTTP client"""
        async with self._client_lock:
            if self._client:
                try:
                    await self._client.aclose()
                except Exception as e:
                    logger.warning(f"Error closing client: {e}")
                finally:
                    self._client = None
                    self._loop = None

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

        title = config.get("title") or config.get("name") or resource_id

        try:
            response = await client.post(
                "/session",
                json={"title": title}
            )
            response.raise_for_status()

            data = response.json()
            session_id = data.get("id")
            if not session_id:
                raise ValueError("OpenCode create_session response missing 'id'")

            logger.info(
                "Created OpenCode session %s for emp_no=%s",
                session_id,
                user_context.get("emp_no", "unknown")
            )
            return session_id

        except (httpx.HTTPError, ValueError) as e:
            logger.error(f"Failed to create OpenCode session: {e}")
            raise

    async def send_message(
        self,
        session_id: str,
        message: str,
        trace_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Send a message to OpenCode session
        Returns the assistant's response text
        """
        client = await self._get_client()

        headers = {}
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        payload: Dict[str, Any] = {
            "parts": [{"type": "text", "text": message}]
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = await client.post(
                f"/session/{session_id}/message",
                json=payload,
                headers=headers
            )
            response.raise_for_status()

            data = response.json()
            assistant_message = self._extract_text_from_parts(data.get("parts", []))

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

        headers = {}
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        try:
            response = await client.get(
                f"/session/{session_id}/message",
                headers=headers
            )
            response.raise_for_status()

            payload = response.json()
            raw_messages = payload if isinstance(payload, list) else []
            messages: List[Message] = []

            for msg in raw_messages:
                info = msg.get("info", {})
                role = info.get("role", "assistant")
                timestamp_raw = info.get("createdAt")
                timestamp = self._parse_iso_datetime(timestamp_raw)
                text = self._extract_text_from_parts(msg.get("parts", []))

                messages.append(Message(role=role, text=text, timestamp=timestamp))

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

    @staticmethod
    def _extract_text_from_parts(parts: List[Dict[str, Any]]) -> str:
        """Extract readable text from OpenCode message parts."""
        text_chunks = []
        for part in parts:
            if part.get("type") == "text" and part.get("text"):
                text_chunks.append(part["text"])
        return "\n".join(text_chunks)

    @staticmethod
    def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
        """Parse ISO-8601 datetime string into datetime object."""
        if not value:
            return None

        try:
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except ValueError:
            logger.warning("Failed to parse message timestamp: %s", value)
            return None
