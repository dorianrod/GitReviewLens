from sqlalchemy.orm import joinedload, subqueryload

from src.domain.entities.pull_request import PullRequest
from src.domain.repositories.pull_requests import PullRequestsRepository
from src.infra.database.postgresql.database import get_db_session
from src.infra.database.postgresql.models.models import Comment as CommentModel
from src.infra.database.postgresql.models.models import PullRequest as PullRequestModel
from src.infra.database.postgresql.models.models import pull_request_approvers
from src.infra.repositories.postgresql.comments import CommentsDatabaseRepository
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository
from src.infra.repositories.postgresql.utils import (
    raise_exception_if_upsert_cannot_be_done,
)


class PullRequestsDatabaseRepository(PullRequestsRepository):
    async def upsert(self, entity: PullRequest, options=None):
        options = options or {}

        await super().upsert(entity, options)

        upsert_developers = options.get("upsert_developers", True)
        upsert_comments = options.get("upsert_comments", True)

        if upsert_developers:
            developer_repository = DeveloperDatabaseRepository(logger=self.logger)
            developers = entity.get_developers()
            for developer in developers:
                await developer_repository.upsert(developer)

        session = get_db_session()
        pull_request = (
            session.query(PullRequestModel)
            .filter(PullRequestModel.id == entity.id)
            .first()
        )
        raise_exception_if_upsert_cannot_be_done(options, pull_request)

        if pull_request is None:
            self.logger.debug("Creating pull request: " + repr(entity))
        else:
            self.logger.debug("Updating pull request: " + repr(entity))

        columns = PullRequestModel.from_entity(entity)
        columns.pop("comments")
        approvers = columns.pop("approvers")
        if pull_request:
            for key in columns:
                setattr(pull_request, key, columns[key])
        else:
            pull_request = PullRequestModel(**columns)
        session.add(pull_request)
        session.commit()

        session.query(pull_request_approvers).where(
            pull_request_approvers.c.pull_request_id == pull_request.id
        ).delete()
        session.commit()
        for approver in approvers:
            session.execute(
                pull_request_approvers.insert().values(
                    pull_request_id=pull_request.id,
                    approver_id=approver.id,
                )
            )
            session.commit()

        if upsert_comments:
            comment_repository = CommentsDatabaseRepository(
                logger=self.logger, git_repository=self.git_repository
            )
            for comment in entity.comments:
                await comment_repository.upsert(
                    comment, {"pull_request": entity, "upsert_pull_request": False}
                )

    async def find_all(self, filters=None):
        filters = filters or {}
        session = get_db_session()

        pull_request_source_id = filters.get("source_id")
        pull_request_id = filters.get("id")
        if pull_request_id:
            query = session.query(PullRequestModel).filter(
                PullRequestModel.id == pull_request_id
            )
        elif pull_request_source_id:
            query = session.query(PullRequestModel).filter(
                PullRequestModel.source_id == pull_request_source_id
            )
        else:
            query = session.query(PullRequestModel)

        query = query.filter(PullRequestModel.repository == self.git_repository.path)

        pull_requests = query.options(
            joinedload(PullRequestModel.created_by),
            subqueryload(PullRequestModel.comments),
            joinedload(PullRequestModel.approvers),
        ).all()

        pull_requests_entities: list[PullRequest] = []
        for pull_request in pull_requests:
            comments = []
            for comment in pull_request.comments:
                comments.append(CommentModel.to_entity(comment))

            pull_request_entity = PullRequestModel.to_entity(pull_request)
            pull_requests_entities.append(pull_request_entity)

        return pull_requests_entities
