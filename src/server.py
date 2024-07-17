import asyncio

import uvicorn

from src.app.create_app import create_app
from src.infra.monitoring.logger import logger


async def main():
    app = await create_app(logger)
    return app


if __name__ == "__main__":
    app = asyncio.run(main())
    uvicorn.run(app, host="0.0.0.0", port=5000)
