from dataclasses import dataclass
from typing import Sequence

from src.common.monitoring.logger import LoggerInterface
from src.common.use_cases.base_use_case import BaseUseCaseWithParameters
from src.domain.entities.developer import Developer
from src.domain.entities.transcoder import Transcoder


@dataclass
class TranscodeDevelopersUseCase(BaseUseCaseWithParameters[Sequence[Developer]]):
    transcoder: Transcoder
    logger: LoggerInterface

    def execute(self, developers: Sequence[Developer]) -> Sequence[Developer]:
        transcoded_developers: list[Developer] = []

        for developer in developers:
            transcoded_developer = Developer.from_dict(developer.to_dict())
            transcoded_developer.full_name = self.transcoder.transcode(
                transcoded_developer.email
            )
            transcoded_developers.append(transcoded_developer)

        return transcoded_developers
