"""Redis storage layer for sessions and launch records"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from ..models import PortalSession, LaunchRecord, SessionBinding, PortalMessage, ContextScope
from ..config import settings


logger = logging.getLogger(__name__)


class RedisStore:
    """Redis storage operations"""

    def __init__(self):
        self.redis_url = settings.redis_url
        self._redis: Optional[Redis] = None
        self._async_redis: Optional[AsyncRedis] = None

    def get_sync_client(self) -> Redis:
        """Get synchronous Redis client"""
        if self._redis is None:
            self._redis = Redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def get_async_client(self) -> AsyncRedis:
        """Get asynchronous Redis client"""
        if self._async_redis is None:
            self._async_redis = AsyncRedis.from_url(self.redis_url, decode_responses=True)
        return self._async_redis

    def close(self):
        """Close connections"""
        if self._redis:
            self._redis.close()
            self._redis = None

    async def close_async(self):
        """Close async connection"""
        if self._async_redis:
            await self._async_redis.close()
            self._async_redis = None

    # Session operations
    async def save_session(self, session: PortalSession) -> bool:
        """Save portal session to Redis"""
        client = await self.get_async_client()

        key = f"portal:session:{session.portal_session_id}"
        session_data = session.model_dump_json()

        try:
            await client.hset(key, mapping={"data": session_data})

            user_key = f"portal:user:{session.user_emp_no}:sessions"
            score = int(session.updated_at.timestamp())
            await client.zadd(user_key, {session.portal_session_id: score})

            logger.info(f"Saved session: {session.portal_session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    async def get_session(self, portal_session_id: str) -> Optional[PortalSession]:
        """Get portal session by ID"""
        client = await self.get_async_client()

        key = f"portal:session:{portal_session_id}"

        try:
            data = await client.hget(key, "data")
            if not data:
                return None

            session_dict = json.loads(data)
            return PortalSession(**session_dict)

        except Exception as e:
            logger.error(f"Failed to get session {portal_session_id}: {e}")
            return None

    async def list_user_sessions(
        self,
        emp_no: str,
        limit: int = 50,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[PortalSession]:
        """List user's sessions sorted by time with optional filters"""
        client = await self.get_async_client()

        user_key = f"portal:user:{emp_no}:sessions"

        try:
            session_ids = await client.zrevrange(user_key, 0, -1)

            sessions = []
            for session_id in session_ids:
                session = await self.get_session(session_id)
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

        except Exception as e:
            logger.error(f"Failed to list sessions for user {emp_no}: {e}")
            return []

    async def delete_session(self, portal_session_id: str) -> bool:
        """Delete a session"""
        client = await self.get_async_client()

        key = f"portal:session:{portal_session_id}"

        try:
            session = await self.get_session(portal_session_id)
            if session:
                user_key = f"portal:user:{session.user_emp_no}:sessions"
                await client.zrem(user_key, portal_session_id)

            await client.delete(key)
            logger.info(f"Deleted session: {portal_session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete session {portal_session_id}: {e}")
            return False

    # Launch operations
    async def save_launch(self, launch: LaunchRecord) -> bool:
        """Save launch record to Redis"""
        client = await self.get_async_client()

        key = f"portal:launch:{launch.launch_id}"
        launch_data = launch.model_dump_json()

        try:
            await client.hset(key, mapping={"data": launch_data})

            user_key = f"portal:user:{launch.user_emp_no}:launches"
            score = int(launch.launched_at.timestamp())
            await client.zadd(user_key, {launch.launch_id: score})

            logger.info(f"Saved launch: {launch.launch_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save launch: {e}")
            return False

    async def get_launch(self, launch_id: str) -> Optional[LaunchRecord]:
        """Get launch record by ID"""
        client = await self.get_async_client()

        key = f"portal:launch:{launch_id}"

        try:
            data = await client.hget(key, "data")
            if not data:
                return None

            launch_dict = json.loads(data)
            return LaunchRecord(**launch_dict)

        except Exception as e:
            logger.error(f"Failed to get launch {launch_id}: {e}")
            return None

    async def list_user_launches(
        self,
        emp_no: str,
        limit: int = 50
    ) -> List[LaunchRecord]:
        """List user's launches sorted by time"""
        client = await self.get_async_client()

        user_key = f"portal:user:{emp_no}:launches"

        try:
            launch_ids = await client.zrevrange(user_key, 0, limit - 1)

            launches = []
            for launch_id in launch_ids:
                launch = await self.get_launch(launch_id)
                if launch:
                    launches.append(launch)

            logger.info(f"Listed {len(launches)} launches for user {emp_no}")
            return launches

        except Exception as e:
            logger.error(f"Failed to list launches for user {emp_no}: {e}")
            return []

    # Binding operations
    async def save_binding(self, binding: SessionBinding) -> bool:
        """Save session binding to Redis"""
        client = await self.get_async_client()

        key = f"portal:binding:{binding.binding_id}"
        binding_data = binding.model_dump_json()

        try:
            await client.hset(key, mapping={"data": binding_data})

            session_key = f"portal:session:{binding.portal_session_id}:bindings"
            score = int(binding.updated_at.timestamp())
            await client.zadd(session_key, {binding.binding_id: score})

            logger.info(f"Saved binding: {binding.binding_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save binding: {e}")
            return False

    async def get_binding(self, binding_id: str) -> Optional[SessionBinding]:
        """Get session binding by ID"""
        client = await self.get_async_client()

        key = f"portal:binding:{binding_id}"

        try:
            data = await client.hget(key, "data")
            if not data:
                return None

            binding_dict = json.loads(data)
            return SessionBinding(**binding_dict)
        except Exception as e:
            logger.error(f"Failed to get binding {binding_id}: {e}")
            return None

    async def get_bindings_by_session(self, portal_session_id: str) -> List[SessionBinding]:
        """Get all bindings for a session"""
        client = await self.get_async_client()

        session_key = f"portal:session:{portal_session_id}:bindings"

        try:
            binding_ids = await client.zrevrange(session_key, 0, -1)
            bindings = []
            for bid in binding_ids:
                binding = await self.get_binding(bid)
                if binding:
                    bindings.append(binding)
            return bindings
        except Exception as e:
            logger.error(f"Failed to get bindings for session {portal_session_id}: {e}")
            return []

    async def delete_binding(self, binding_id: str) -> bool:
        """Delete a session binding"""
        client = await self.get_async_client()

        key = f"portal:binding:{binding_id}"

        try:
            binding = await self.get_binding(binding_id)
            if binding:
                session_key = f"portal:session:{binding.portal_session_id}:bindings"
                await client.zrem(session_key, binding_id)

            await client.delete(key)
            logger.info(f"Deleted binding: {binding_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete binding {binding_id}: {e}")
            return False

    # Message operations
    async def save_message(self, message: PortalMessage) -> bool:
        """Save portal message to Redis"""
        client = await self.get_async_client()

        key = f"portal:message:{message.message_id}"
        message_data = message.model_dump_json()

        try:
            await client.hset(key, mapping={"data": message_data})

            session_key = f"portal:session:{message.portal_session_id}:messages"
            score = int(message.created_at.timestamp())
            await client.zadd(session_key, {message.message_id: score})

            logger.info(f"Saved message: {message.message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return False

    async def get_message(self, message_id: str) -> Optional[PortalMessage]:
        """Get portal message by ID"""
        client = await self.get_async_client()

        key = f"portal:message:{message_id}"

        try:
            data = await client.hget(key, "data")
            if not data:
                return None

            message_dict = json.loads(data)
            return PortalMessage(**message_dict)
        except Exception as e:
            logger.error(f"Failed to get message {message_id}: {e}")
            return None

    async def list_session_messages(
        self,
        portal_session_id: str,
        limit: int = 500,
        offset: int = 0
    ) -> List[PortalMessage]:
        """List messages for a session in chronological order"""
        client = await self.get_async_client()

        session_key = f"portal:session:{portal_session_id}:messages"

        try:
            message_ids = await client.zrange(session_key, offset, offset + limit - 1)
            messages = []
            for mid in message_ids:
                msg = await self.get_message(mid)
                if msg:
                    messages.append(msg)
            return messages
        except Exception as e:
            logger.error(f"Failed to list messages for session {portal_session_id}: {e}")
            return []

    async def delete_session_messages(self, portal_session_id: str) -> bool:
        """Delete all messages for a session"""
        client = await self.get_async_client()

        session_key = f"portal:session:{portal_session_id}:messages"

        try:
            message_ids = await client.zrange(session_key, 0, -1)
            if message_ids:
                for mid in message_ids:
                    await client.delete(f"portal:message:{mid}")
                await client.delete(session_key)
            logger.info(f"Deleted messages for session: {portal_session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete messages for session {portal_session_id}: {e}")
            return False

    # Context operations
    async def save_context(self, context: ContextScope) -> bool:
        """Save context scope to Redis"""
        client = await self.get_async_client()

        key = f"portal:context:{context.context_id}"
        context_data = context.model_dump_json()

        try:
            await client.hset(key, mapping={"data": context_data})

            scope_key = f"portal:scope:{context.scope_type}:{context.scope_key}"
            score = int(context.updated_at.timestamp())
            await client.zadd(scope_key, {context.context_id: score})

            logger.info(f"Saved context: {context.context_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
            return False

    async def get_context(self, context_id: str) -> Optional[ContextScope]:
        """Get context scope by ID"""
        client = await self.get_async_client()

        key = f"portal:context:{context_id}"

        try:
            data = await client.hget(key, "data")
            if not data:
                return None

            context_dict = json.loads(data)
            return ContextScope(**context_dict)
        except Exception as e:
            logger.error(f"Failed to get context {context_id}: {e}")
            return None

    async def get_contexts_by_scope(
        self,
        scope_type: str,
        scope_key: str,
        limit: int = 10
    ) -> List[ContextScope]:
        """Get contexts by scope type and key"""
        client = await self.get_async_client()

        scope_key_redis = f"portal:scope:{scope_type}:{scope_key}"

        try:
            context_ids = await client.zrevrange(scope_key_redis, 0, limit - 1)
            contexts = []
            for cid in context_ids:
                ctx = await self.get_context(cid)
                if ctx:
                    contexts.append(ctx)
            return contexts
        except Exception as e:
            logger.error(f"Failed to get contexts for scope {scope_type}:{scope_key}: {e}")
            return []

    async def delete_context(self, context_id: str) -> bool:
        """Delete a context scope"""
        client = await self.get_async_client()

        key = f"portal:context:{context_id}"

        try:
            context = await self.get_context(context_id)
            if context:
                scope_key_redis = f"portal:scope:{context.scope_type}:{context.scope_key}"
                await client.zrem(scope_key_redis, context_id)

            await client.delete(key)
            logger.info(f"Deleted context: {context_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete context {context_id}: {e}")
            return False


# Global Redis store instance
redis_store = RedisStore()
