import asyncio
from datetime import datetime

from src.common.utils.worker import concurrency_aio


async def test_concurrency():
    await run_test(
        messages=["mes1", "mes2", "mes3"],
        max_concurrency=5,
        difference_max=0.2,
    )


async def test_no_concurrency():
    await run_test(
        messages=["mes1", "mes2"],
        max_concurrency=1,
        difference_min=1,
    )


async def test_do_not_execute_all_actions_with_iterator():
    start_times = []

    @concurrency_aio(max_concurrency=2)
    async def fn(msg):
        start_times.append(datetime.now())
        await asyncio.sleep(1)
        return msg

    iterator = fn.run(["mes1", "mes2", "mes3"])

    async for row in iterator:
        result = row
        break

    await asyncio.sleep(0.5)

    assert (
        len(start_times) == 2
    )  # Concurrency is 2, so the "mes2" has already been executed
    assert result in ["mes1", "mes2"]

    async for row in iterator:
        result = row
        break

    assert result == "mes2"  # we only run one value for iterator

    # All tasks have been executed
    assert len(start_times) == 3


async def test_decorator_with_several_parameters():
    @concurrency_aio(max_concurrency=2)
    async def fn(msg, suffix):
        await asyncio.sleep(1)
        return msg + str(suffix)

    result = await fn.run_all([("mes1", "-a"), ("mes2", "-b")])
    assert result == ["mes1-a", "mes2-b"]


async def test_decorator_in_class():
    class MyClass:
        start_times = []

        @concurrency_aio(max_concurrency=2)
        async def fn(self, msg):
            self.start_times.append(datetime.now())
            await asyncio.sleep(1)
            return msg

    cls = MyClass()

    result = await cls.fn.run_all(cls, ["msg1", "msg2"])

    assert sorted(result) == ["msg1", "msg2"]


async def test_decorator_in_class_without_self():
    start_times = []

    class MyClass:
        @concurrency_aio(max_concurrency=2)
        async def fn(self, msg):
            assert self is None

            start_times.append(datetime.now())
            await asyncio.sleep(1)
            return msg

    cls = MyClass()

    result = await cls.fn.run_all(["msg1", "msg2"])

    assert sorted(result) == ["msg1", "msg2"]


def assert_concurrent(start_times, ref_difference=0.2):
    assert len(start_times) > 1, "Not enough messages to test concurrency"
    max_start_time = max(start_times)
    min_start_time = min(start_times)
    difference = (max_start_time - min_start_time).total_seconds()
    assert (
        difference < ref_difference
    ), f"Tasks did not start concurrently, difference: {difference} seconds"


def assert_no_concurrent(start_times, ref_difference):
    assert len(start_times) > 1, "Not enough messages to test concurrency"
    max_start_time = max(start_times)
    min_start_time = min(start_times)
    difference = (max_start_time - min_start_time).total_seconds()
    assert (
        difference > ref_difference
    ), f"Tasks did start concurrently, difference: {difference} seconds"


async def run_test(messages, max_concurrency, difference_max=None, difference_min=None):
    start_times = []

    @concurrency_aio(max_concurrency=max_concurrency)
    async def wrapped_fn(msg):
        start_times.append(datetime.now())
        await asyncio.sleep(1)
        return msg

    result = await wrapped_fn.run_all(messages)
    if difference_max:
        assert_concurrent(start_times, difference_max)
    elif difference_min:
        assert_no_concurrent(start_times, difference_min)
    assert sorted(result) == sorted(messages)
