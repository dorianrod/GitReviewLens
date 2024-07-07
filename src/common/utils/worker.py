import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Optional, Protocol, cast

from src.common.utils.async_iterator_transformer import AsyncTransformIterator


class Worker(ABC):
    def __init__(self, max_concurrency: Optional[int] = None):
        self.semaphore = asyncio.Semaphore(max_concurrency) if max_concurrency else None
        self.max_concurrency = max_concurrency

    @abstractmethod
    async def process_task(self, task: Any, queue: asyncio.Queue) -> Any:
        """Override this method to process a task."""
        raise NotImplementedError

    async def run_task(self, queue: asyncio.Queue):
        while True:
            task = await queue.get()
            try:
                if task is None:
                    return

                result = await self.process_task(task, queue)
                return result
            finally:
                queue.task_done()

    async def add_task(self, queue: asyncio.Queue, running_tasks: list[Any]):
        if self.semaphore:
            async with self.semaphore:
                task = asyncio.create_task(self.run_task(queue))
                running_tasks.append(task)
        else:
            task = asyncio.create_task(self.run_task(queue))
            running_tasks.append(task)

    async def work(self):
        return WorkerIterator(self)


class WorkerIterator:
    def __init__(self, worker: Worker):
        self.worker = worker
        self.running_tasks: list[Any] = []
        self.queue: asyncio.Queue = asyncio.Queue()
        self.stop_processing = False

    async def initialize_tasks(self):
        size_initial_tasks = int(
            min(self.worker.max_concurrency or float('inf'), self.queue.qsize())
        )
        for _ in range(size_initial_tasks):
            await self.worker.add_task(self.queue, self.running_tasks)

    async def gather_results(self):
        await self.initialize_tasks()

        while self.running_tasks:
            done, _ = await asyncio.wait(
                self.running_tasks, return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                result = await task
                self.running_tasks.remove(task)

                if result is None:
                    self.stop_processing = True

                if result:
                    yield result

                if self.stop_processing:
                    if self.running_tasks:
                        await asyncio.gather(
                            *self.running_tasks, return_exceptions=True
                        )
                        self.running_tasks = []
                    return

                if self.queue.empty():
                    continue

                await self.worker.add_task(self.queue, self.running_tasks)

    def __aiter__(self):
        self.result_iterator = self.gather_results()
        return self

    async def __anext__(self):
        return await self.result_iterator.__anext__()


class ConcurrencyFunction(Protocol):
    def __call__(self, msg: Any) -> Any: ...
    def run(self, msgs: list[Any]) -> AsyncTransformIterator: ...
    def run_all(self, msgs: list[Any]) -> Awaitable[list[Any]]: ...


def concurrency_aio(max_concurrency: int):
    class ExtractOriginalData(AsyncTransformIterator):
        async def transform(self, data):
            return data[0]

    def decorator(func: Callable[..., Any]):
        def get_iterator(self, parameters=[]):
            parent_self = self
            if not parameters:
                parameters = parent_self
                parent_self = None

            func_signature = inspect.signature(func)
            func_params = list(func_signature.parameters)

            class MyWorker(Worker):
                async def process_task(self, task: Any, queue: asyncio.Queue) -> Any:
                    if isinstance(task, tuple):
                        args = [*task]
                    else:
                        args = [task]

                    if func_params[0] != "self":
                        result = await func(*args)
                    else:
                        result = await func(parent_self, *args)
                    return (result, True)  # if result is None, it would stop iteration

            worker = MyWorker(max_concurrency=max_concurrency)
            worker_iterator = WorkerIterator(worker)

            for task in parameters:
                worker_iterator.queue.put_nowait(task)

            return ExtractOriginalData(worker_iterator)

        async def run_all(self, parameters=[]):
            if not parameters:
                parameters = self
                self = None

            iterator = get_iterator(self, parameters)
            return [result async for result in iterator]

        decorated_func = cast(ConcurrencyFunction, func)
        setattr(decorated_func, 'run', get_iterator)
        setattr(decorated_func, 'run_all', run_all)

        return decorated_func

    return decorator
