import functools
import time


def monitor(label=""):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.logger.info(f"Starting '{label}'...")
            start_time = time.time()
            result = func(self, *args, **kwargs)
            end_time = time.time()
            self.logger.info(f"Finished '{label}' in {end_time - start_time} seconds")
            return result

        return wrapper

    return decorator
