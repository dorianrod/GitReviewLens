import asyncio
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from src.common.utils.async_iterator_filter import AsyncFilterEmptyIterator
from src.common.utils.worker import Worker
from src.infra.requests.fetch import async_fetch


class RequestException(Exception):
    pass


class PaginatorWorker(Worker, ABC):
    def __init__(
        self,
        items_per_page: int,
        logger,
        headers: Optional[dict[str, str]] = None,
        max_concurrency: int = 10,
        timeout: Optional[int] = None,
    ):
        super().__init__(max_concurrency)
        assert max_concurrency is not None, "max_concurrency is mandatory"
        self.headers = headers or {}
        self.timeout = timeout
        self.logger = logger
        self.items_per_page = items_per_page
        self.page = 0
        self.page_lock = asyncio.Lock()

    @abstractmethod
    async def get_url(self, page: int) -> str:
        pass

    async def process_data(
        self, data: Any, options: Optional[dict[str, Any]] = None
    ) -> Tuple[Any, bool]:
        return data, True

    async def fetch_data(
        self, url: str, options: Optional[dict[str, Any]] = None
    ) -> Tuple[Any, bool]:
        """Fetch data from the given URL and process it."""
        self.logger.info(f"Fetching {url}")

        data = await async_fetch(url, headers=self.headers, timeout=self.timeout)
        return await self.process_data(data, options)

    async def add_url_to_queue(
        self, queue: asyncio.Queue, options: Optional[dict[str, Any]] = None
    ):
        async with self.page_lock:
            url = await self.get_url(self.page)
            self.page += 1
            await queue.put((url, options))

    async def process_task(self, task: Any, queue: asyncio.Queue) -> Any:
        url, options = task
        data, should_continue = await self.fetch_data(url, options)
        if should_continue:
            await self.add_url_to_queue(queue, options)
        return data, should_continue

    async def fetch(self, options: Optional[dict[str, Any]] = None):
        iterator = await self.work()
        for _ in range(self.max_concurrency):  # type: ignore
            await self.add_url_to_queue(iterator.queue, options)

        return AsyncFilterEmptyIterator(iterator)
