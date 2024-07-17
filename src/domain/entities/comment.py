from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from src.common.utils.date import format_to_iso, parse_date
from src.common.utils.string import get_hash
from src.domain.entities.common import BaseEntity

from .developer import Developer


@dataclass
class Comment(BaseEntity):
    developer: Developer
    content: str
    creation_date: datetime
    pull_request_id: Optional[str] = None

    def clone(self):
        return Comment.from_dict(self.to_dict())

    @property
    def id(self):
        combined_string = f"{self.content}.{str(self.creation_date)}"
        return get_hash(combined_string)

    @property
    def size(self):
        return len(self.content or "")  # if self.content else 0

    @classmethod
    def from_dict(cls, data):
        developer_data = data.get("developer")
        if not isinstance(developer_data, Developer):
            developer = Developer.from_dict(developer_data)
        else:
            developer = Developer.from_dict(developer_data.to_dict())

        return cls(
            pull_request_id=data.get("pull_request_id"),
            developer=developer,
            content=data.get("content") or "",
            creation_date=parse_date(data.get("creation_date")),
        )

    def to_dict(self):
        comment_dict = asdict(self)
        comment_dict["id"] = self.id
        comment_dict["size"] = self.size
        comment_dict["creation_date"] = format_to_iso(self.creation_date)
        comment_dict["pull_request_id"] = self.pull_request_id
        return comment_dict

    def __repr__(self):
        return f"<Comment by {repr(self.developer)} - size: {self.size}>"
