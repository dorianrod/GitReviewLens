from src.common.utils.async_iterator_transformer import AsyncTransformIterator


class AsyncFilterMultiplyIterator(AsyncTransformIterator):
    async def transform(self, value):
        return value * 2


async def test_apply_transform_to_iterator():
    async def generator():
        for i in range(4):
            yield i

    filtered_iter = AsyncFilterMultiplyIterator(generator())
    values = [v async for v in filtered_iter]
    assert values == [0, 2, 4, 6]
