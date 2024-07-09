import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager


class EntityLockManager:
    def __init__(self, id=None):
        self.locks = defaultdict(asyncio.Lock)
        self.id = id

    @asynccontextmanager
    async def lock(self, entity):
        lock = self.locks[hash((entity.__class__.__name__, entity.id))]
        await lock.acquire()
        try:
            yield
        finally:
            lock.release()


lock_manager = EntityLockManager("main")
