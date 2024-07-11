import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Optional, Protocol, cast

from src.common.utils.async_iterator_filter import AsyncFilterEmptyIterator
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
        stop_message = None, False
        while True:
            if queue.empty():
                return stop_message

            try:
                task = await queue.get()
                if task is None:
                    return stop_message

                result = await self.process_task(task, queue)
                return result
            finally:
                queue.task_done()

    async def add_task(self, queue: asyncio.Queue, running_tasks: list[Any]):
        loop = asyncio.get_event_loop()
        if self.semaphore:
            async with self.semaphore:
                task = loop.create_task(self.run_task(queue))
                running_tasks.append(task)
        else:
            task = loop.create_task(self.run_task(queue))
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
                was_stop_processing = self.stop_processing

                result, should_continue = await task
                self.running_tasks.remove(task)

                if not should_continue:
                    self.stop_processing = True

                yield result

                if not was_stop_processing or not self.queue.empty():
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
    # class ExtractOriginalData(AsyncTransformIterator):
    #     async def transform(self, data):
    #         return data[0]

    def decorator(func: Callable[..., Any]):
        def get_parameters(parent_self, parameters):
            if parameters is None:
                parameters = parent_self
                parent_self = None
            return parent_self, parameters

        def get_iterator(self, parameters=None):
            parent_self, parameters = get_parameters(self, parameters)

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

            return AsyncFilterEmptyIterator(
                worker_iterator
            )  # ExtractOriginalData(worker_iterator)

        async def run_all(self, parameters=None):
            parent_self, parameters = get_parameters(self, parameters)
            iterator = get_iterator(parent_self, parameters)
            return [result async for result in iterator]

        decorated_func = cast(ConcurrencyFunction, func)
        setattr(decorated_func, 'run', get_iterator)
        setattr(decorated_func, 'run_all', run_all)

        return decorated_func

    return decorator
