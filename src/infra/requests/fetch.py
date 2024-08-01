import aiohttp

from src.common.utils.async_retry import async_retry


async def async_fetch(url, headers={}, timeout=30, max_retries: int = 3, client=None):
    @async_retry(max_retries=max_retries)
    async def _fetch():
        nonlocal client

        if client:
            async with client.get(url) as response:
                response.raise_for_status()
                return await response.json()
        else:
            async with aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout) if timeout else None,
            ) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()

    return await _fetch()
