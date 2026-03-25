"""In-memory storage layer for sessions and launch records (Redis alternative)"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import OrderedDict

from ..models import PortalSession, LaunchRecord


logger = logging.getLogger(__name__)


class MemoryStore:
    """
    In-memory storage for sessions and launch records
    Simple alternative to Redis for development/testing
    """

    def __init__(self):
        # Use OrderedDict with maxsize for LRU-like behavior
        self._sessions: OrderedDict[str, PortalSession] = OrderedDict()
        self._launches: OrderedDict[str, LaunchRecord] = OrderedDict()
        self._user_sessions: Dict[str, List[str]] = {}
        self._user_launches: Dict[str, List[str]] = {}

        # Limits to prevent unbounded growth
        self._max_sessions = 1000
        self._max_launches = 1000
        self._max_user_sessions = 100
        self._max_user_launches = 100

    # Session operations
    async def save_session(self, session: PortalSession) -> bool:
        """Save portal session to memory"""
        try:
            # Add to sessions dict
            self._sessions[session.portal_session_id] = session

            # Manage size
            if len(self._sessions) > self._max_sessions:
                # Remove oldest
                oldest_id = next(iter(self._sessions))
                del self._sessions[oldest_id]

            # Add to user's session list
            emp_no = session.user_emp_no
            if emp_no not in self._user_sessions:
                self._user_sessions[emp_no] = []

            # Remove if already exists
            if session.portal_session_id in self._user_sessions[emp_no]:
                self._user_sessions[emp_no].remove(session.portal_session_id)

            # Add to front
            self._user_sessions[emp_no].insert(0, session.portal_session_id)

            # Manage size per user
            if len(self._user_sessions[emp_no]) > self._max_user_sessions:
                self._user_sessions[emp_no] = self._user_sessions[emp_no][:self._max_user_sessions]

            logger.info(f"Saved session: {session.portal_session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    async def get_session(self, portal_session_id: str) -> Optional[PortalSession]:
        """Get portal session by ID"""
        return self._sessions.get(portal_session_id)

    async def list_user_sessions(
        self,
        emp_no: str,
        limit: int = 50
    ) -> List[PortalSession]:
        """List user's sessions sorted by time"""
        session_ids = self._user_sessions.get(emp_no, [])
        sessions = []

        for session_id in session_ids[:limit]:
            session = self._sessions.get(session_id)
            if session:
                sessions.append(session)

        logger.info(f"Listed {len(sessions)} sessions for user {emp_no}")
        return sessions

    async def delete_session(self, portal_session_id: str) -> bool:
        """Delete a session"""
        try:
            # Get session first to remove from user's list
            session = self._sessions.get(portal_session_id)
            if session:
                emp_no = session.user_emp_no
                if emp_no in self._user_sessions:
                    if portal_session_id in self._user_sessions[emp_no]:
                        self._user_sessions[emp_no].remove(portal_session_id)

            # Remove from sessions
            if portal_session_id in self._sessions:
                del self._sessions[portal_session_id]

            logger.info(f"Deleted session: {portal_session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete session {portal_session_id}: {e}")
            return False

    # Launch operations
    async def save_launch(self, launch: LaunchRecord) -> bool:
        """Save launch record to memory"""
        try:
            # Add to launches dict
            self._launches[launch.launch_id] = launch

            # Manage size
            if len(self._launches) > self._max_launches:
                # Remove oldest
                oldest_id = next(iter(self._launches))
                del self._launches[oldest_id]

            # Add to user's launch list
            emp_no = launch.user_emp_no
            if emp_no not in self._user_launches:
                self._user_launches[emp_no] = []

            # Remove if already exists
            if launch.launch_id in self._user_launches[emp_no]:
                self._user_launches[emp_no].remove(launch.launch_id)

            # Add to front
            self._user_launches[emp_no].insert(0, launch.launch_id)

            # Manage size per user
            if len(self._user_launches[emp_no]) > self._max_user_launches:
                self._user_launches[emp_no] = self._user_launches[emp_no][:self._max_user_launches]

            logger.info(f"Saved launch: {launch.launch_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save launch: {e}")
            return False

    async def get_launch(self, launch_id: str) -> Optional[LaunchRecord]:
        """Get launch record by ID"""
        return self._launches.get(launch_id)

    async def list_user_launches(
        self,
        emp_no: str,
        limit: int = 50
    ) -> List[LaunchRecord]:
        """List user's launches sorted by time"""
        launch_ids = self._user_launches.get(emp_no, [])
        launches = []

        for launch_id in launch_ids[:limit]:
            launch = self._launches.get(launch_id)
            if launch:
                launches.append(launch)

        logger.info(f"Listed {len(launches)} launches for user {emp_no}")
        return launches

    def clear_all(self):
        """Clear all data (for testing)"""
        self._sessions.clear()
        self._launches.clear()
        self._user_sessions.clear()
        self._user_launches.clear()
        logger.info("Cleared all data from memory store")


# Global memory store instance
memory_store = MemoryStore()
