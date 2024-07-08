import asyncio
import functools
import time


def monitor(label=""):
    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            self.logger.info(f"Starting '{label}'...")
            start_time = time.time()
            result = func(self, *args, **kwargs)
            end_time = time.time()
            self.logger.info(f"Finished '{label}' in {end_time - start_time} seconds")
            return result

        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            self.logger.info(f"Starting '{label}'...")
            start_time = time.time()
            result = await func(self, *args, **kwargs)
            end_time = time.time()
            self.logger.info(f"Finished '{label}' in {end_time - start_time} seconds")
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
