import asyncio
import random
from functools import wraps
from typing import Awaitable, Callable, TypeVar

T = TypeVar('T')


class MaxRetry(Exception):
    message = "Max retry for task"


def async_retry(
    max_retries: int = 3,
    min_retry_delay: float = 0.1,
    max_retry_delay: float = 3.0,
    exceptions: tuple = (Exception,),
    raise_original_exception=True,
):
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:  # type: ignore
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        if raise_original_exception:
                            raise e
                        raise MaxRetry() from e
                    retry_delay = random.uniform(min_retry_delay, max_retry_delay)
                    await asyncio.sleep(retry_delay)

        return wrapper

    return decorator
