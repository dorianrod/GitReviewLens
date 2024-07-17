from dataclasses import dataclass
from datetime import datetime

from src.common.utils.date import format_to_iso, get_business_time_diff, parse_date
from src.common.utils.json import recursive_asdict
from src.common.utils.string import get_hash
from src.domain.entities.common import BaseEntity, eq
from src.domain.entities.repository import Repository
from src.settings import settings

from .comment import Comment
from .developer import Developer


@dataclass
class PullRequest(BaseEntity):
    source_id: str

    approvers: list[Developer]
    comments: list[Comment]
    created_by: Developer
    creation_date: datetime
    completion_date: datetime

    title: str

    source_branch: str
    target_branch: str

    commit: str
    previous_commit: str

    git_repository: Repository

    type: str

    @property
    def id(self):
        combined_string = f"{self.git_repository.path}.{self.source_id}"
        return get_hash(combined_string)

    @property
    def merge_time(self):
        return max(
            0,
            get_business_time_diff(
                self.creation_date,
                self.completion_date,
                settings.calendar,
                settings.business_time_range,
            ),
        )

    @property
    def first_comment_delay(self):
        first_comment_date = None
        for comment in self.comments:
            if first_comment_date is None or comment.creation_date < first_comment_date:
                first_comment_date = comment.creation_date

        if first_comment_date is None:
            return None

        return max(
            0,
            get_business_time_diff(
                self.creation_date,
                first_comment_date,
                settings.calendar,
                settings.business_time_range,
            ),
        )

    def get_developers(self) -> list[Developer]:
        developers = {}
        developers[self.created_by.id] = self.created_by
        for approver in self.approvers:
            developers[approver.id] = approver
        for comment in self.comments:
            commenter = comment.developer
            developers[commenter.id] = commenter
        return list(developers.values())

    @classmethod
    def from_dict(cls, data):
        creation_date = parse_date(data.get("creation_date"))
        completion_date = parse_date(data.get("completion_date"))
        created_by = (
            Developer.from_dict(data.get("created_by"))
            if not isinstance(data.get("created_by"), Developer)
            else data.get("created_by").clone()
        )

        pull_request = cls(
            source_id=str(data["source_id"]),
            type=data.get("type") or "feature",
            approvers=[
                Developer.from_dict(d) if not isinstance(d, Developer) else d.clone()
                for d in data.get("approvers", [])
            ],
            comments=[],
            created_by=created_by,
            creation_date=creation_date,
            completion_date=completion_date,
            title=data.get("title"),
            git_repository=Repository.parse(data.get("git_repository")),
            source_branch=data.get("source_branch"),
            target_branch=data.get("target_branch"),
            commit=data.get("commit"),
            previous_commit=data.get("previous_commit"),
        )

        pull_request.comments = [
            (
                Comment.from_dict({**c, "pull_request_id": pull_request.id})
                if not isinstance(c, Comment)
                else c.clone()
            )
            for c in data.get("comments", [])
        ]

        return pull_request

    def to_dict(self):
        pull_request_dict = recursive_asdict(self)
        pull_request_dict["approvers"] = sorted(
            pull_request_dict["approvers"], key=lambda x: x["email"]
        )
        pull_request_dict["comments"] = sorted(
            pull_request_dict["comments"], key=lambda x: x["creation_date"]
        )
        pull_request_dict["merge_time"] = self.merge_time
        pull_request_dict["first_comment_delay"] = self.first_comment_delay
        pull_request_dict["completion_date"] = format_to_iso(self.completion_date)
        pull_request_dict["creation_date"] = format_to_iso(self.creation_date)
        pull_request_dict["git_repository"] = self.git_repository.path
        return pull_request_dict

    def __repr__(self):
        return f"<PullRequest {str(self.git_repository)} - {self.source_id} - {self.title}>"

    def __eq__(self, obj):
        # For unknown reason : tests fails if not override
        return eq(self, obj)
