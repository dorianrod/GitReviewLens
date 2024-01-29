from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, declarative_base, relationship

from src.common.utils.string import get_hash
from src.domain.entities.comment import Comment as CommentEntity
from src.domain.entities.developer import Developer as DeveloperEntity
from src.domain.entities.feature import Feature as FeatureEntity
from src.domain.entities.pull_request import PullRequest as PullRequestEntity
from src.domain.entities.repository import Repository

Base = declarative_base()


class Developer(Base):  # type: ignore
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

    def from_entity(developer: DeveloperEntity):
        return {
            "id": developer.id,
            "email": developer.email,
            "name": developer.full_name,
        }


class Comment(Base):  # type: ignore
    __tablename__ = "comments"

    id = Column(String, primary_key=True)

    content = Column(String, nullable=False)
    creation_date = Column(
        DateTime,
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
            content=data.content,
            creation_date=data.creation_date,
            developer=Developer.to_entity(data.developer) if data.developer else None,
        )

    @staticmethod
    def from_entity(
        comment: CommentEntity, pull_request: Optional[PullRequestEntity] = None
    ):
        comment_dict = comment.to_dict()
        return {
            "id": get_hash(comment.id + pull_request.id if pull_request else ""),
            "content": comment.content,
            "creation_date": comment_dict["creation_date"],
            "pull_request_id": pull_request.id if pull_request else None,
            "developer_id": comment.developer.id,
        }


pull_request_approvers = Table(
    "pull_request_approvers",
    Base.metadata,  # type: ignore
    Column("pull_request_id", ForeignKey("pull_requests.id")),
    Column("approver_id", ForeignKey("developers.id")),
)


class PullRequest(Base):  # type: ignore
    __tablename__ = "pull_requests"

    id = Column(String, primary_key=True)

    source_id = Column(String)
    repository = Column(String)

    completion_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = Column(String, ForeignKey("developers.id"), nullable=False)
    approvers: Mapped[List[Developer]] = relationship(secondary=pull_request_approvers)
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
            approvers=[Developer.to_entity(approver) for approver in data.approvers],
            comments=[Comment.to_entity(comment) for comment in data.comments],
        )

    @staticmethod
    def from_entity(pull_request: PullRequestEntity):
        pr_dict = pull_request.to_dict()
        return {
            "id": pull_request.id,
            "source_id": pr_dict["source_id"],
            "repository": pr_dict["git_repository"],
            "type": pr_dict["type"],
            "title": pr_dict["title"],
            "completion_date": pr_dict["completion_date"],
            "creation_date": pr_dict["creation_date"],
            "merge_time": pr_dict["merge_time"],
            "first_comment_delay": pr_dict["first_comment_delay"],
            "source_branch": pr_dict["source_branch"],
            "target_branch": pr_dict["target_branch"],
            "previous_commit": pr_dict["previous_commit"],
            "commit": pr_dict["commit"],
            "created_by_id": pr_dict["created_by"]["email"],
            "approvers": pull_request.approvers or [],
            "comments": [],
        }

    def __repr__(self):
        return f"<PullRequest(id={self.source_id}, repository={self.repository})>"


class Feature(Base):  # type: ignore
    __tablename__ = "features"

    id = Column(String, primary_key=True)

    commit = Column(String)

    date = Column(DateTime, nullable=False)

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
    def from_entity(entity: FeatureEntity):
        return {
            "id": entity.id,
            "repository": entity.git_repository.path,
            "commit": entity.commit,
            "date": entity.date.isoformat(),
            "developer_id": entity.developer.id,
            "count_deleted_lines": entity.count_deleted_lines,
            "count_inserted_lines": entity.count_inserted_lines,
            "dmm_unit_complexity": entity.dmm_unit_complexity,
            "dmm_unit_interfacing": entity.dmm_unit_interfacing,
            "dmm_unit_size": entity.dmm_unit_size,
            "modified_files": entity.modified_files,
        }

    @staticmethod
    def to_entity(data):
        return FeatureEntity(
            git_repository=Repository.parse(data.repository),
            commit=data.commit,
            date=data.date,
            developer=Developer.to_entity(data.developer) if data.developer else None,
            count_deleted_lines=data.count_deleted_lines,
            count_inserted_lines=data.count_inserted_lines,
            dmm_unit_complexity=data.dmm_unit_complexity,
            dmm_unit_interfacing=data.dmm_unit_interfacing,
            dmm_unit_size=data.dmm_unit_size,
            modified_files=data.modified_files,
        )

    def __repr__(self):
        return f"<Feature(id={self.id}, commit={self.commit}, repository={self.repository.path})>"
