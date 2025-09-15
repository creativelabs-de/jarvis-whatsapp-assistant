import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # For development, create a mock client
            self.redis_client = MockRedisClient()
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        try:
            if self.redis_client:
                return await self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
        return None
    
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """Set key-value pair with optional expiration"""
        try:
            if self.redis_client:
                await self.redis_client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
    
    async def setex(self, key: str, expire: int, value: str):
        """Set key-value pair with expiration"""
        await self.set(key, value, expire)
    
    async def delete(self, key: str):
        """Delete key"""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            if self.redis_client:
                return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
        return False

class MockRedisClient:
    """Mock Redis client for development when Redis is not available"""
    def __init__(self):
        self.data = {}
    
    async def get(self, key: str) -> Optional[str]:
        return self.data.get(key)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None):
        self.data[key] = value
    
    async def delete(self, key: str):
        self.data.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        return key in self.data
    
    async def close(self):
        pass

# Global Redis client instance
redis_client = RedisClient()
