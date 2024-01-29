import datetime
from typing import Optional, Sequence, TypedDict, cast

from src.common.monitoring.logger import LoggerInterface
from src.common.use_cases.base_use_case import BaseUseCaseWithParameters
from src.common.utils.date import is_in_range, parse_date
from src.domain.entities.developer import Developer
from src.domain.entities.feature import Feature
from src.domain.entities.pull_request import PullRequest
from src.domain.entities.repository import Repository
from src.domain.factories.comment import CommentFactory
from src.domain.factories.developer import DeveloperFactory
from src.domain.factories.feature import FeatureFactory
from src.domain.factories.pull_request import PullRequestFactory
from src.domain.factories.repository import RepositoryFactory


class Filters(TypedDict):
    start_date: Optional[str | datetime.datetime]
    end_date: Optional[str | datetime.datetime]


class AnonymizeDatasetUseCase(
    BaseUseCaseWithParameters[tuple[Sequence[PullRequest], Sequence[Feature]]]
):
    __anonymized_developer: dict[str, Developer]
    __anonymized_repository: dict[str, Repository]

    logger: LoggerInterface

    def __init__(
        self, logger: LoggerInterface, git_repository: Optional[Repository | str] = None
    ):
        self.logger = logger
        self.__anonymized_developer = {}
        self.__anonymized_repository = {}
        self.__git_repository = (
            Repository.parse(git_repository) if git_repository else None
        )

    def get_anonymized_developer(self, developer: Developer) -> Developer:
        anonymized_developer = self.__anonymized_developer.get(developer.id, None)
        if anonymized_developer is None:
            anonymized_developer = DeveloperFactory.create_developer()
            self.__anonymized_developer[developer.id] = anonymized_developer

        return anonymized_developer

    def get_anonymized_repository(self, repository: Repository) -> Repository:
        if self.__git_repository is not None:
            return self.__git_repository

        anonymized_repository = self.__anonymized_repository.get(str(repository), None)
        if anonymized_repository is None:
            anonymized_repository = RepositoryFactory.create_repository()
            self.__anonymized_repository[str(repository)] = anonymized_repository

        return anonymized_repository

    def execute(
        self,
        pull_requests: Sequence[PullRequest],
        features: Sequence[Feature],
        options: Optional[Filters] = None,
    ) -> tuple[Sequence[PullRequest], Sequence[Feature]]:
        options = cast(
            Filters,
            {
                **(options or {}),
            },
        )

        start_date = parse_date(options.get("start_date"))
        end_date = parse_date(options.get("end_date"))

        anonymized_pull_requests: list[PullRequest] = []
        anonymized_features: list[Feature] = []

        for pull_request in pull_requests:
            if not is_in_range(pull_request.creation_date, start_date, end_date):
                continue

            approvers = [
                self.get_anonymized_developer(approver)
                for approver in pull_request.approvers
            ]

            comments = [
                CommentFactory.create_comment(
                    creation_date=comment.creation_date,
                    content_length=len(comment.content),
                    developer=self.get_anonymized_developer(comment.developer),
                )
                for comment in pull_request.comments
            ]

            anonymized_pull_request = PullRequestFactory.create_pull_request(
                **{
                    **pull_request.to_dict(),
                    "title": None,
                    "target_branch": None,
                    "source_branch": None,
                    "git_repository": self.get_anonymized_repository(
                        pull_request.git_repository
                    ),
                    "created_by": self.get_anonymized_developer(
                        pull_request.created_by
                    ),
                    "approvers": approvers,
                    "comments": comments,
                }
            )

            anonymized_pull_requests.append(anonymized_pull_request)

        for feature in features:
            if not is_in_range(feature.date, start_date, end_date):
                continue

            anonymized_feature = FeatureFactory.create_feature(
                **{
                    **feature.to_dict(),
                    "modified_files": [],
                    "developer": self.get_anonymized_developer(feature.developer),
                    "git_repository": self.get_anonymized_repository(
                        feature.git_repository
                    ),
                }
            )
            anonymized_features.append(anonymized_feature)

        return anonymized_pull_requests, anonymized_features
