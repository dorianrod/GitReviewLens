import asyncio

from src.app.controllers.extract_transform_load.load_features_from_repositories import (
    LoadFeaturesController,
)
from src.app.controllers.extract_transform_load.load_pull_requests_from_remote_origins import (
    LoadPullRequestsFromRemoteOriginController,
)
from src.app.controllers.extract_transform_load.transcode_developers_in_database import (
    TranscodeDevelopersInDatabaseController,
)
from src.app.controllers.extract_transform_load.transcode_pull_requests_in_database import (
    TranscodePullRequestsInDatabaseController,
)
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command


async def main():
    load_pull_request = Command(
        LoadPullRequestsFromRemoteOriginController(logger=LoggerDefault())
    )

    transcode_developers = Command(
        TranscodeDevelopersInDatabaseController(logger=LoggerDefault())
    )

    transcode_pull_requests = Command(
        TranscodePullRequestsInDatabaseController(logger=LoggerDefault())
    )

    load_features = Command(
        LoadFeaturesController(
            logger=LoggerDefault(),
        )
    )

    await asyncio.gather(
        asyncio.create_task(load_pull_request.launch()),
    )

    # Slower to execute, but not needed to display some dashboards
    await load_features.launch(
        options={"process_ddm": False, "get_modified_files": True},
    )

    await asyncio.gather(
        asyncio.create_task(transcode_pull_requests.launch()),
        asyncio.create_task(transcode_developers.launch()),
    )


asyncio.run(main())
