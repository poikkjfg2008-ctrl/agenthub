"""Base adapter protocol and interfaces"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models import Message


class ExecutionAdapter(ABC):
    """
    Base adapter protocol for all execution adapters
    All adapters must implement these methods
    """

    @abstractmethod
    async def create_session(
        self,
        resource_id: str,
        user_context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        """
        Create a new session in the backend engine
        Returns the engine session ID
        """
        pass

    @abstractmethod
    async def send_message(
        self,
        session_id: str,
        message: str,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Send a message to the session
        Returns the assistant's response
        """
        pass

    @abstractmethod
    async def get_messages(
        self,
        session_id: str,
        trace_id: Optional[str] = None
    ) -> List[Message]:
        """
        Get message history for a session
        """
        pass

    @abstractmethod
    async def close_session(
        self,
        session_id: str,
        trace_id: Optional[str] = None
    ) -> bool:
        """
        Close a session
        """
        pass
