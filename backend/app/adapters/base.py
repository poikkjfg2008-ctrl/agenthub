"""Base adapter protocol and interfaces"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from fastapi import UploadFile

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
    async def send_message_stream(
        self,
        session_id: str,
        message: str,
        trace_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Send a message to the session with streaming response
        Yields chunks of the assistant's response
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

    @abstractmethod
    async def upload_file(
        self,
        session_id: str,
        file: UploadFile,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to the session
        Returns file metadata including URL
        """
        pass
