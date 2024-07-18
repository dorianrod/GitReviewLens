import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager


class EntityLockManager:
    def __init__(self, id=None):
        self.locks = defaultdict(asyncio.Lock)
        self.id = id

    @asynccontextmanager
    async def lock(self, *entities):
        locks = [
            self.locks[hash((entity.__class__.__name__, entity.id))]
            for entity in entities
        ]

        await asyncio.gather(*[lock.acquire() for lock in locks])

        try:
            yield
        finally:
            for lock in locks:
                lock.release()


lock_manager = EntityLockManager("main")
