import pytest

from src.common.utils.async_retry import MaxRetry, async_retry


async def success_func():
    return "Success"


failure_count = 0


async def failing_func():
    global failure_count
    failure_count += 1
    if failure_count < 3:
        raise ValueError("Simulated failure")
    return "Success after retries"


async def always_failing_func():
    raise ValueError("Always fails")


async def test_successful_execution():
    decorated_func = async_retry()(success_func)
    result = await decorated_func()
    assert result == "Success"


async def test_retry_success():
    global failure_count
    failure_count = 0
    decorated_func = async_retry(max_retries=3)(failing_func)
    result = await decorated_func()
    assert result == "Success after retries"
    assert failure_count == 3


async def test_max_retries_reached():
    decorated_func = async_retry(max_retries=3)(always_failing_func)
    with pytest.raises(MaxRetry):
        await decorated_func()


async def test_custom_exceptions():
    async def custom_exception_func():
        raise KeyError("Custom exception")

    decorated_func = async_retry(max_retries=2, exceptions=(KeyError,))(
        custom_exception_func
    )
    with pytest.raises(MaxRetry):
        await decorated_func()


async def test_non_matching_exception():
    async def type_error_func():
        raise TypeError("Type error")

    decorated_func = async_retry(max_retries=2, exceptions=(ValueError,))(
        type_error_func
    )
    with pytest.raises(TypeError):
        await decorated_func()
