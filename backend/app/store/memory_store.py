"""In-memory storage layer for sessions and launch records (Redis alternative)"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import OrderedDict

from ..models import PortalSession, LaunchRecord, SessionBinding, PortalMessage, ContextScope


logger = logging.getLogger(__name__)


class MemoryStore:
    """
    In-memory storage for sessions, launch records, bindings, messages, and contexts
    Simple alternative to Redis for development/testing
    """

    def __init__(self):
        # Use OrderedDict with maxsize for LRU-like behavior
        self._sessions: OrderedDict[str, PortalSession] = OrderedDict()
        self._launches: OrderedDict[str, LaunchRecord] = OrderedDict()
        self._bindings: OrderedDict[str, SessionBinding] = OrderedDict()
        self._messages: OrderedDict[str, PortalMessage] = OrderedDict()
        self._contexts: OrderedDict[str, ContextScope] = OrderedDict()

        self._user_sessions: Dict[str, List[str]] = {}
        self._user_launches: Dict[str, List[str]] = {}
        self._user_contexts: Dict[str, List[str]] = {}
        self._session_messages: Dict[str, List[str]] = {}
        self._session_bindings: Dict[str, List[str]] = {}

        # Limits to prevent unbounded growth
        self._max_sessions = 1000
        self._max_launches = 1000
        self._max_bindings = 2000
        self._max_messages = 10000
        self._max_contexts = 2000
        self._max_user_sessions = 100
        self._max_user_launches = 100
        self._max_session_messages = 200

    # Session operations
    async def save_session(self, session: PortalSession) -> bool:
        """Save portal session to memory"""
        try:
            self._sessions[session.portal_session_id] = session

            if len(self._sessions) > self._max_sessions:
                oldest_id = next(iter(self._sessions))
                del self._sessions[oldest_id]

            emp_no = session.user_emp_no
            if emp_no not in self._user_sessions:
                self._user_sessions[emp_no] = []

            if session.portal_session_id in self._user_sessions[emp_no]:
                self._user_sessions[emp_no].remove(session.portal_session_id)

            self._user_sessions[emp_no].insert(0, session.portal_session_id)

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
        limit: int = 50,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[PortalSession]:
        """List user's sessions sorted by time with optional filters"""
        session_ids = self._user_sessions.get(emp_no, [])
        sessions = []

        for session_id in session_ids:
            session = self._sessions.get(session_id)
            if not session:
                continue
            if resource_id and session.resource_id != resource_id:
                continue
            if resource_type and session.resource_type != resource_type:
                continue
            if status and session.status != status:
                continue
            sessions.append(session)
            if len(sessions) >= limit:
                break

        logger.info(f"Listed {len(sessions)} sessions for user {emp_no}")
        return sessions

    async def delete_session(self, portal_session_id: str) -> bool:
        """Delete a session"""
        try:
            session = self._sessions.get(portal_session_id)
            if session:
                emp_no = session.user_emp_no
                if emp_no in self._user_sessions:
                    if portal_session_id in self._user_sessions[emp_no]:
                        self._user_sessions[emp_no].remove(portal_session_id)

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
            self._launches[launch.launch_id] = launch

            if len(self._launches) > self._max_launches:
                oldest_id = next(iter(self._launches))
                del self._launches[oldest_id]

            emp_no = launch.user_emp_no
            if emp_no not in self._user_launches:
                self._user_launches[emp_no] = []

            if launch.launch_id in self._user_launches[emp_no]:
                self._user_launches[emp_no].remove(launch.launch_id)

            self._user_launches[emp_no].insert(0, launch.launch_id)

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

    # Binding operations
    async def save_binding(self, binding: SessionBinding) -> bool:
        """Save session binding to memory"""
        try:
            self._bindings[binding.binding_id] = binding

            if len(self._bindings) > self._max_bindings:
                oldest_id = next(iter(self._bindings))
                del self._bindings[oldest_id]

            session_id = binding.portal_session_id
            if session_id not in self._session_bindings:
                self._session_bindings[session_id] = []

            if binding.binding_id in self._session_bindings[session_id]:
                self._session_bindings[session_id].remove(binding.binding_id)

            self._session_bindings[session_id].insert(0, binding.binding_id)

            logger.info(f"Saved binding: {binding.binding_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save binding: {e}")
            return False

    async def get_binding(self, binding_id: str) -> Optional[SessionBinding]:
        """Get session binding by ID"""
        return self._bindings.get(binding_id)

    async def get_bindings_by_session(self, portal_session_id: str) -> List[SessionBinding]:
        """Get all bindings for a session"""
        binding_ids = self._session_bindings.get(portal_session_id, [])
        bindings = []
        for bid in binding_ids:
            binding = self._bindings.get(bid)
            if binding:
                bindings.append(binding)
        return bindings

    async def delete_binding(self, binding_id: str) -> bool:
        """Delete a session binding"""
        try:
            binding = self._bindings.get(binding_id)
            if binding:
                session_id = binding.portal_session_id
                if session_id in self._session_bindings:
                    if binding_id in self._session_bindings[session_id]:
                        self._session_bindings[session_id].remove(binding_id)
                del self._bindings[binding_id]
            logger.info(f"Deleted binding: {binding_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete binding {binding_id}: {e}")
            return False

    # Message operations
    async def save_message(self, message: PortalMessage) -> bool:
        """Save portal message to memory"""
        try:
            self._messages[message.message_id] = message

            if len(self._messages) > self._max_messages:
                oldest_id = next(iter(self._messages))
                del self._messages[oldest_id]

            session_id = message.portal_session_id
            if session_id not in self._session_messages:
                self._session_messages[session_id] = []

            if message.message_id in self._session_messages[session_id]:
                self._session_messages[session_id].remove(message.message_id)

            self._session_messages[session_id].append(message.message_id)

            if len(self._session_messages[session_id]) > self._max_session_messages:
                self._session_messages[session_id] = self._session_messages[session_id][-self._max_session_messages:]

            logger.info(f"Saved message: {message.message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return False

    async def get_message(self, message_id: str) -> Optional[PortalMessage]:
        """Get portal message by ID"""
        return self._messages.get(message_id)

    async def list_session_messages(
        self,
        portal_session_id: str,
        limit: int = 500,
        offset: int = 0
    ) -> List[PortalMessage]:
        """List messages for a session in chronological order"""
        message_ids = self._session_messages.get(portal_session_id, [])
        messages = []
        for mid in message_ids[offset:offset + limit]:
            msg = self._messages.get(mid)
            if msg:
                messages.append(msg)
        return messages

    async def delete_session_messages(self, portal_session_id: str) -> bool:
        """Delete all messages for a session"""
        try:
            message_ids = self._session_messages.pop(portal_session_id, [])
            for mid in message_ids:
                self._messages.pop(mid, None)
            logger.info(f"Deleted messages for session: {portal_session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete messages for session {portal_session_id}: {e}")
            return False

    # Context operations
    async def save_context(self, context: ContextScope) -> bool:
        """Save context scope to memory"""
        try:
            self._contexts[context.context_id] = context

            if len(self._contexts) > self._max_contexts:
                oldest_id = next(iter(self._contexts))
                del self._contexts[oldest_id]

            key = context.scope_key
            if key not in self._user_contexts:
                self._user_contexts[key] = []

            if context.context_id in self._user_contexts[key]:
                self._user_contexts[key].remove(context.context_id)

            self._user_contexts[key].insert(0, context.context_id)

            logger.info(f"Saved context: {context.context_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
            return False

    async def get_context(self, context_id: str) -> Optional[ContextScope]:
        """Get context scope by ID"""
        return self._contexts.get(context_id)

    async def get_contexts_by_scope(
        self,
        scope_type: str,
        scope_key: str,
        limit: int = 10
    ) -> List[ContextScope]:
        """Get contexts by scope type and key"""
        context_ids = self._user_contexts.get(scope_key, [])
        contexts = []
        for cid in context_ids[:limit]:
            ctx = self._contexts.get(cid)
            if ctx and ctx.scope_type == scope_type:
                contexts.append(ctx)
        return contexts

    async def delete_context(self, context_id: str) -> bool:
        """Delete a context scope"""
        try:
            context = self._contexts.get(context_id)
            if context:
                key = context.scope_key
                if key in self._user_contexts:
                    if context_id in self._user_contexts[key]:
                        self._user_contexts[key].remove(context_id)
                del self._contexts[context_id]
            logger.info(f"Deleted context: {context_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete context {context_id}: {e}")
            return False

    def clear_all(self):
        """Clear all data (for testing)"""
        self._sessions.clear()
        self._launches.clear()
        self._bindings.clear()
        self._messages.clear()
        self._contexts.clear()
        self._user_sessions.clear()
        self._user_launches.clear()
        self._user_contexts.clear()
        self._session_messages.clear()
        self._session_bindings.clear()
        logger.info("Cleared all data from memory store")


# Global memory store instance
memory_store = MemoryStore()
