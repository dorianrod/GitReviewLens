import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

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
        headers: Dict[str, str] = {},
        max_concurrency: int = 10,
        timeout: Optional[int] = None,
    ):
        super().__init__(max_concurrency)
        assert max_concurrency is not None, "max_concurrency is mandatory"
        self.headers = headers
        self.timeout = timeout
        self.logger = logger
        self.items_per_page = items_per_page
        self.page = 0
        self.page_lock = asyncio.Lock()

    @abstractmethod
    async def get_url(self, page: int) -> str:
        pass

    async def process_data(self, data: Any) -> Tuple[Any, bool]:
        return data, True

    async def fetch_data(self, url: str) -> Tuple[Any, bool]:
        """Fetch data from the given URL and process it."""
        self.logger.info(f"Fetching {url}")

        data = await async_fetch(url, headers=self.headers, timeout=self.timeout)
        return await self.process_data(data)

    async def add_url_to_queue(self, queue: asyncio.Queue):
        async with self.page_lock:
            url = await self.get_url(self.page)
            self.page += 1
            await queue.put(url)

    async def process_task(self, task: str, queue: asyncio.Queue) -> Any:
        url = task
        data, should_continue = await self.fetch_data(url)
        if should_continue:
            await self.add_url_to_queue(queue)
        return data, should_continue

    async def fetch(self):
        iterator = await self.work()
        for _ in range(self.max_concurrency):  # type: ignore
            await self.add_url_to_queue(iterator.queue)

        return AsyncFilterEmptyIterator(iterator)
