from dataclasses import dataclass
from typing import Sequence

from src.common.monitoring.logger import LoggerInterface
from src.common.use_cases.base_use_case import BaseUseCaseWithParameters
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.transcoder import Transcoder


@dataclass
class TranscodePullRequestsUseCase(BaseUseCaseWithParameters[Sequence[PullRequest]]):
    transcoder: Transcoder
    logger: LoggerInterface

    async def execute(
        self, pull_requests: Sequence[PullRequest]
    ) -> Sequence[PullRequest]:
        transcoded_pull_requests: list[PullRequest] = []

        for pull_request in pull_requests:
            transcoded_pull_request = PullRequest.from_dict(pull_request.to_dict())

            transcoded_pull_request.type = (
                self.transcoder.transcode_by_startvalue(pull_request.source_branch)
                or "Unknown"
            )

            transcoded_pull_requests.append(transcoded_pull_request)

        return transcoded_pull_requests
