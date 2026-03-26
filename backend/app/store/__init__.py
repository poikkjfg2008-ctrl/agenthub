"""Storage module - exports appropriate store based on configuration"""

from ..config import settings

# Use Redis or in-memory store based on configuration
if settings.use_redis:
    from .redis_store import redis_store as store
else:
    from .memory_store import memory_store as store

__all__ = ['store']
