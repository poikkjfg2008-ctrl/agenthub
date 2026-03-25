"""Redis storage layer for sessions and launch records"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from ..models import PortalSession, LaunchRecord, UserCtx
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

            # Add to user's session list (sorted by time)
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
        limit: int = 50
    ) -> List[PortalSession]:
        """List user's sessions sorted by time"""
        client = await self.get_async_client()

        user_key = f"portal:user:{emp_no}:sessions"

        try:
            # Get recent session IDs
            session_ids = await client.zrevrange(user_key, 0, limit - 1)

            sessions = []
            for session_id in session_ids:
                session = await self.get_session(session_id)
                if session:
                    sessions.append(session)

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
            # Get session first to remove from user's list
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

            # Add to user's launch list (sorted by time)
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
            # Get recent launch IDs
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


# Global Redis store instance
redis_store = RedisStore()
