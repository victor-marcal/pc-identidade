import json
from contextlib import asynccontextmanager

from pydantic import RedisDsn
from redis.asyncio import Redis


class RedisAsyncioAdapter:

    def __init__(self, redis_url: RedisDsn):
        self.redis_url = str(redis_url)
        self.redis_client = Redis.from_url(self.redis_url)

    async def aclose(self):
        await self.redis_client.aclose()

    async def exists(self, k: str) -> bool:
        count = await self.redis_client.exists(k)
        ok = count > 0
        return ok

    async def get_str(self, key: str) -> str:
        v = await self.redis_client.get(key)
        if v is not None:
            v = v.decode()
        return v

    async def set_str(self, k: str, v: any, expires_in_seconds: int | None = None):
        if v is None:
            await self.delete(k)
            return

        if not isinstance(v, str):
            v = str(v)

        await self.redis_client.set(k, v, expires_in_seconds)

    async def get_json(self, key: str) -> dict | list | int | None:
        v = await self.get_str(key)
        if v is not None:
            v = json.loads(v)
        return v

    async def set_json(
        self,
        key: str,
        v: dict | list | int | None,
        expires_in_seconds: int | None = None,
    ):
        if v is not None:
            v = json.dumps(v)
        await self.set_str(key, v, expires_in_seconds)

    async def delete(self, key: str):
        await self.redis_client.delete(key)

    @asynccontextmanager
    async def locks(
        self,
        k: str,
        timeout_in_seconds: float | None = None,
        blocking_timeout_in_seconds: float | None = None,
        prefix_lock: str = "lock_",
    ):
        key = f"{prefix_lock}{k}"
        async with self.redis_client.lock(
            key,
            timeout=timeout_in_seconds,
            blocking_timeout=blocking_timeout_in_seconds,
        ) as locker:
            yield locker
