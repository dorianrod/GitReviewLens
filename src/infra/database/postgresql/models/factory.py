import weakref
from abc import abstractmethod
from datetime import datetime
from typing import List, Optional, cast

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, declarative_base, relationship

from src.common.utils.string import get_hash
from src.domain.entities.comment import Comment as CommentEntity
from src.domain.entities.common import BaseEntity
from src.domain.entities.developer import Developer as DeveloperEntity
from src.domain.entities.feature import Feature as FeatureEntity
from src.domain.entities.pull_request import PullRequest as PullRequestEntity
from src.domain.entities.repository import Repository


def build_models(schema):
    Base = declarative_base(metadata=MetaData(schema=schema))

    class BaseModel(Base):  # type: ignore
        __abstract__ = True

        @staticmethod
        @abstractmethod
        def to_entity(data):
            pass

        @staticmethod
        @abstractmethod
        def from_entity(entity: BaseEntity, options: Optional[dict] = None):
            pass

    class Developer(BaseModel):
        __tablename__ = "developers"

        id = Column(String, primary_key=True)
        name = Column(String, nullable=False)
        email = Column(String, nullable=False)

        pull_requests = relationship("PullRequest", back_populates="created_by")
        features = relationship("Feature", back_populates="developer")
        comments = relationship("Comment", back_populates="developer")

        @staticmethod
        def to_entity(data):
            return DeveloperEntity(full_name=data.name, email=data.email)

        @staticmethod
        def from_entity(entity: BaseEntity, options=None):
            developer = cast(DeveloperEntity, entity)
            return {
                "id": developer.id,
                "email": developer.email,
                "name": developer.full_name,
            }

    class Comment(BaseModel):
        __tablename__ = "comments"

        id = Column(String, primary_key=True)

        content = Column(String, nullable=False)
        creation_date = Column(
            DateTime(timezone=True),
            nullable=False,
            default=datetime.utcnow,
        )
        developer_id = Column(String, ForeignKey("developers.id"), nullable=False)
        developer = relationship(
            "Developer",
            back_populates="comments",
            primaryjoin="Comment.developer_id == Developer.id",
        )

        pull_request_id = Column(String, ForeignKey("pull_requests.id"), nullable=False)
        pull_request = relationship(
            "PullRequest",
            back_populates="comments",
            primaryjoin="Comment.pull_request_id == PullRequest.id",
        )

        @staticmethod
        def to_entity(data):
            return CommentEntity(
                pull_request_id=data.pull_request_id,
                content=data.content,
                creation_date=data.creation_date,
                developer=(
                    Developer.to_entity(data.developer) if data.developer else None
                ),
            )

        @staticmethod
        def from_entity(entity: BaseEntity, options=None):
            comment = cast(CommentEntity, entity)
            options = options or {}
            pull_request: Optional[PullRequestEntity] = options.get("pull_request")
            return {
                "id": get_hash(
                    comment.id
                    + (
                        comment.pull_request_id
                        or (pull_request.id if pull_request else "")
                    )
                ),
                "content": comment.content,
                "creation_date": comment.creation_date,
                "pull_request_id": (
                    comment.pull_request_id
                    or (pull_request.id if pull_request else None)
                ),
                "developer_id": comment.developer.id,
            }

    pull_request_approvers = Table(
        "pull_request_approvers",
        Base.metadata,  # type: ignore
        Column("pull_request_id", ForeignKey("pull_requests.id")),
        Column("approver_id", ForeignKey("developers.id")),
    )

    class PullRequest(BaseModel):
        __tablename__ = "pull_requests"

        id = Column(String, primary_key=True)

        source_id = Column(String)
        repository = Column(String)

        completion_date = Column(
            DateTime(timezone=True), nullable=False, default=datetime.utcnow
        )
        creation_date = Column(
            DateTime(timezone=True), nullable=False, default=datetime.utcnow
        )
        created_by_id = Column(String, ForeignKey("developers.id"), nullable=False)
        approvers: Mapped[List[Developer]] = relationship(
            secondary=pull_request_approvers
        )
        merge_time = Column(Float)
        first_comment_delay = Column(Float)
        comments = relationship("Comment", back_populates="pull_request")

        source_branch = Column(String)
        target_branch = Column(String)
        commit = Column(String)
        previous_commit = Column(String)

        title = Column(String)
        type = Column(String)

        created_by = relationship("Developer", back_populates="pull_requests")

        @staticmethod
        def to_entity(data):
            return PullRequestEntity(
                source_id=data.source_id,
                git_repository=Repository.parse(data.repository),
                type=data.type,
                title=data.title,
                completion_date=data.completion_date,
                creation_date=data.creation_date,
                source_branch=data.source_branch,
                target_branch=data.target_branch,
                previous_commit=data.previous_commit,
                commit=data.commit,
                created_by=Developer.to_entity(data.created_by),
                approvers=(
                    [Developer.to_entity(approver) for approver in data.approvers]
                    if data.approvers
                    else []
                ),
                comments=(
                    [Comment.to_entity(comment) for comment in data.comments]
                    if data.comments
                    else []
                ),
            )

        @staticmethod
        def from_entity(entity: BaseEntity, options=None):
            pull_request = cast(PullRequestEntity, entity)
            options = options or {}
            many_to_many = options.get("many_to_many", False)

            values = {
                "id": pull_request.id,
                "source_id": pull_request.source_id,
                "repository": pull_request.git_repository.path,
                "type": pull_request.type,
                "title": pull_request.title,
                "completion_date": pull_request.completion_date,
                "creation_date": pull_request.creation_date,
                "merge_time": pull_request.merge_time,
                "first_comment_delay": pull_request.first_comment_delay,
                "source_branch": pull_request.source_branch,
                "target_branch": pull_request.target_branch,
                "previous_commit": pull_request.previous_commit,
                "commit": pull_request.commit,
                "created_by_id": pull_request.created_by.email,
            }

            if many_to_many:
                values["approvers"] = [
                    approver.email for approver in pull_request.approvers
                ]
                values["comments"] = ([],)  # TODO see if usefull

            return values

        def __repr__(self):
            return f"<PullRequest(id={self.source_id}, repository={self.repository})>"

    class Feature(BaseModel):
        __tablename__ = "features"

        id = Column(String, primary_key=True)

        commit = Column(String)

        date = Column(DateTime(timezone=True), nullable=False)

        count_deleted_lines = Column(Integer)
        count_inserted_lines = Column(Integer)
        dmm_unit_complexity = Column(Float)
        dmm_unit_interfacing = Column(Float)
        dmm_unit_size = Column(Float)
        modified_files = Column(JSON)

        developer_id = Column(String, ForeignKey("developers.id"))
        developer = relationship("Developer", back_populates="features")

        repository = Column(String)

        @staticmethod
        def from_entity(entity: BaseEntity, options=None):
            feature = cast(FeatureEntity, entity)
            return {
                "id": feature.id,
                "repository": feature.git_repository.path,
                "commit": feature.commit,
                "date": feature.date,
                "developer_id": feature.developer.id,
                "count_deleted_lines": feature.count_deleted_lines,
                "count_inserted_lines": feature.count_inserted_lines,
                "dmm_unit_complexity": feature.dmm_unit_complexity,
                "dmm_unit_interfacing": feature.dmm_unit_interfacing,
                "dmm_unit_size": feature.dmm_unit_size,
                "modified_files": feature.modified_files,
            }

        @staticmethod
        def to_entity(data):
            return FeatureEntity(
                git_repository=Repository.parse(data.repository),
                commit=data.commit,
                date=data.date,
                developer=(
                    Developer.to_entity(data.developer) if data.developer else None
                ),
                count_deleted_lines=data.count_deleted_lines,
                count_inserted_lines=data.count_inserted_lines,
                dmm_unit_complexity=data.dmm_unit_complexity,
                dmm_unit_interfacing=data.dmm_unit_interfacing,
                dmm_unit_size=data.dmm_unit_size,
                modified_files=data.modified_files,
            )

        def __repr__(self):
            return f"<Feature(id={self.id}, commit={self.commit}, repository={self.repository.path})>"

    models = weakref.WeakValueDictionary(
        {
            "BaseModel": BaseModel,
            "Base": Base,
            "Developer": Developer,
            "Feature": Feature,
            "Comment": Comment,
            "PullRequest": PullRequest,
            "pull_request_approvers": pull_request_approvers,
        }
    )

    for Model in models.values():
        setattr(Model, "models", models)

    return {key: value for key, value in models.items()}
