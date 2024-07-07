from typing import AsyncIterator


class AsyncTransformIterator:
    def __init__(self, async_iterator: AsyncIterator):
        self.async_iterator = async_iterator

    async def transform(data):
        return data

    def __aiter__(self):
        self.async_iterator.__aiter__()
        return self

    async def __anext__(self):
        try:
            item = await self.async_iterator.__anext__()
            return await self.transform(item)
        except StopAsyncIteration:
            raise StopAsyncIteration
