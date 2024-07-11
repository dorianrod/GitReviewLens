from typing import AsyncIterator


class AsyncFilterIterator:
    def __init__(self, async_iterator: AsyncIterator):
        self.async_iterator = async_iterator

    async def filter(self, data):
        return True

    def __aiter__(self):
        self.async_iterator.__aiter__()
        return self

    async def __anext__(self):
        while True:
            try:
                item = await self.async_iterator.__anext__()
                if await self.filter(item):
                    return item
            except StopAsyncIteration:
                raise StopAsyncIteration


class AsyncFilterEmptyIterator(AsyncFilterIterator):
    async def filter(self, value):
        return value is not None and value != []
