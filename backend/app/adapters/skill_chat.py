"""Skill Chat adapter for skill-based conversations"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .opencode import OpenCodeAdapter
from ..models import Message


logger = logging.getLogger(__name__)


class SkillChatAdapter(ExecutionAdapter):
    """
    Adapter for skill-based conversations
    Wraps OpenCodeAdapter with skill-specific behavior
    """

    def __init__(self):
        self.opencode_adapter = OpenCodeAdapter()

    async def create_session(
        self,
        resource_id: str,
        user_context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        """
        Create a new skill chat session
        Includes skill_name in metadata
        """
        # Add skill-specific metadata to config
        skill_config = config.copy()
        skill_config["skill_name"] = config.get("skill_name", resource_id)

        # Create session via OpenCode adapter
        session_id = await self.opencode_adapter.create_session(
            resource_id,
            user_context,
            skill_config
        )

        logger.info(f"Created skill chat session: {session_id} for skill: {config.get('skill_name')}")
        return session_id

    async def send_message(
        self,
        session_id: str,
        message: str,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Send a message to skill chat session
        Delegates to OpenCode adapter
        """
        return await self.opencode_adapter.send_message(session_id, message, trace_id)

    async def get_messages(
        self,
        session_id: str,
        trace_id: Optional[str] = None
    ) -> List[Message]:
        """
        Get message history from skill chat session
        Delegates to OpenCode adapter
        """
        return await self.opencode_adapter.get_messages(session_id, trace_id)

    async def close_session(
        self,
        session_id: str,
        trace_id: Optional[str] = None
    ) -> bool:
        """
        Close skill chat session
        Delegates to OpenCode adapter
        """
        return await self.opencode_adapter.close_session(session_id, trace_id)

    async def close(self):
        """Close underlying adapter"""
        await self.opencode_adapter.close()
