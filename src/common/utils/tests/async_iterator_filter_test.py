from src.common.utils.async_iterator_filter import AsyncFilterIterator


class AsyncFilterNoneIterator(AsyncFilterIterator):
    async def filter(self, value):
        return value is not None


async def test_filters_iterators_depending_on_filter_function():
    async def generator():
        for i in range(6):
            yield i if i % 2 else None

    filtered_iter = AsyncFilterNoneIterator(generator())
    values = [v async for v in filtered_iter]
    assert values == [1, 3, 5]
