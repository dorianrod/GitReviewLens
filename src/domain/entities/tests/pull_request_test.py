from datetime import datetime

import pytest

from src.common.utils.date import parse_date
from src.domain.entities.repository import Repository

from ..comment import Comment
from ..developer import Developer
from ..pull_request import PullRequest


@pytest.fixture(scope="function", autouse=True)
def mock_settings(mocker, mock_git_settings):
    mocker.patch(
        "src.domain.entities.pull_request.settings",
        mock_git_settings,
    )


def test_pullrequest_creation(
    fixture_developer_dict, fixture_developer_2_dict, fixture_comment_dict
):
    pullrequest = PullRequest(
        git_repository=Repository.parse("orga/myrepo"),
        comments=[Comment.from_dict(fixture_comment_dict)],
        completion_date=datetime.fromisoformat("2023-01-02T01:12:17"),
        creation_date=datetime.fromisoformat("2023-01-01T01:12:17"),
        created_by=Developer.from_dict(fixture_developer_dict),
        title="feat 1",
        type="feat",
        source_id="1",
        approvers=[Developer.from_dict(fixture_developer_2_dict)],
        commit="new",
        previous_commit="prev",
        source_branch="feat",
        target_branch="master",
    )
    assert pullrequest.comments == [Comment.from_dict(fixture_comment_dict)]
    assert pullrequest.comments == [Comment.from_dict(fixture_comment_dict)]
    assert pullrequest.created_by == Developer.from_dict(fixture_developer_dict)
    assert pullrequest.source_id == "1"
    assert pullrequest.type == "feat"
    assert pullrequest.title == "feat 1"
    assert pullrequest.git_repository.path == "orga/myrepo"
    assert pullrequest.creation_date == parse_date("2023-01-01T01:12:17")
    assert pullrequest.completion_date == parse_date("2023-01-02T01:12:17")
    assert pullrequest.commit == "new"
    assert pullrequest.previous_commit == "prev"
    assert pullrequest.source_branch == "feat"
    assert pullrequest.target_branch == "master"


def test_pullrequest_from_dict(fixture_pull_request_dict):
    pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
    assert pullrequest.source_id == "10"
    assert pullrequest.title == "feat 1"
    assert pullrequest.type == "feat"
    assert pullrequest.creation_date == parse_date(
        fixture_pull_request_dict["creation_date"]
    )
    assert pullrequest.completion_date == parse_date(
        fixture_pull_request_dict["completion_date"]
    )
    assert pullrequest.git_repository == Repository.parse("orga/myrepo")
    assert pullrequest.source_branch == "feat/myfeat"
    assert pullrequest.target_branch == "master"
    assert pullrequest.previous_commit == "prev"
    assert pullrequest.type == "feat"
    assert pullrequest.commit == "new"
    assert pullrequest.merge_time == 1639
    assert pullrequest.approvers == [
        Developer.from_dict(fixture_pull_request_dict["approvers"][0]),
        Developer.from_dict(fixture_pull_request_dict["approvers"][1]),
    ]
    assert pullrequest.comments == [
        Comment.from_dict(
            {
                **fixture_pull_request_dict["comments"][0],
                "pull_request_id": pullrequest.id,
            }
        ),
        Comment.from_dict(
            {
                **fixture_pull_request_dict["comments"][1],
                "pull_request_id": pullrequest.id,
            }
        ),
    ]


def test_pullrequest_to_dict(fixture_pull_request_dict):
    pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
    assert pullrequest.to_dict() == {
        **fixture_pull_request_dict,
        "comments": [
            Comment.from_dict({**c, "pull_request_id": pullrequest.id}).to_dict()
            for c in fixture_pull_request_dict["comments"]
        ],
        "approvers": [
            Developer.from_dict(v).to_dict()
            for v in fixture_pull_request_dict["approvers"]
        ],
        "created_by": Developer.from_dict(
            fixture_pull_request_dict["created_by"]
        ).to_dict(),
        "creation_date": "2023-10-25T11:10:13Z",
        "completion_date": "2023-10-30T11:30:00Z",
        "first_comment_delay": 1,
        "merge_time": 1639.0,
        "type": "feat",
    }


def test_pullrequest_comparison(fixture_pull_request_dict):
    pullrequest_1 = PullRequest.from_dict(fixture_pull_request_dict)
    pullrequest_2 = PullRequest.from_dict(fixture_pull_request_dict)
    pullrequest_3 = PullRequest.from_dict(fixture_pull_request_dict)
    pullrequest_3.source_id = 1

    assert pullrequest_1 == pullrequest_2
    assert pullrequest_1 != pullrequest_3


class TestMergeTime:
    def test_merge_time_created_outside_business_hours(
        self,
        fixture_pull_request_dict,
    ):
        pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
        pullrequest.creation_date = datetime.fromisoformat("2023-10-27T05:00:00")
        pullrequest.completion_date = datetime.fromisoformat("2023-10-27T11:00:00")
        assert pullrequest.merge_time == (11 - 9) * 60

    def test_merge_time_completed_outside_business_hours(
        self,
        fixture_pull_request_dict,
    ):
        pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
        pullrequest.creation_date = datetime.fromisoformat("2023-10-27T17:00:00")
        pullrequest.completion_date = datetime.fromisoformat("2023-10-27T20:00:00")
        assert pullrequest.merge_time == (18 - 17) * 60

    def test_merge_time_over_weekend(
        self,
        fixture_pull_request_dict,
    ):
        pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
        pullrequest.creation_date = datetime.fromisoformat("2023-10-27T17:00:00")
        pullrequest.completion_date = datetime.fromisoformat("2023-10-30T12:00:00")
        assert pullrequest.merge_time == (1 + (12 - 9)) * 60

    def test_merge_time_over_weeks(
        self,
        fixture_pull_request_dict,
    ):
        pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
        pullrequest.creation_date = datetime.fromisoformat("2023-10-27T17:00:00")
        pullrequest.completion_date = datetime.fromisoformat("2023-11-03T17:00:00")
        # 1 week - 1 day off
        assert pullrequest.merge_time == ((5 - 1) * (18 - 9)) * 60


class TestFirstComment:
    def test_commented_outside_business_hours(self, fixture_pull_request_dict):
        pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
        pullrequest.creation_date = datetime.fromisoformat("2023-10-27T17:00:00")
        pullrequest.comments[0].creation_date = datetime.fromisoformat(
            "2024-01-01T11:00:00"
        )
        pullrequest.comments[1].creation_date = datetime.fromisoformat(
            "2023-10-27T20:00:00"
        )
        assert pullrequest.first_comment_delay == (18 - 17) * 60

    def test_commented_over_weekend(
        self,
        fixture_pull_request_dict,
    ):
        pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
        pullrequest.creation_date = datetime.fromisoformat("2023-10-27T17:00:00")
        pullrequest.comments[0].creation_date = datetime.fromisoformat(
            "2024-01-01T11:00:00"
        )
        pullrequest.comments[1].creation_date = datetime.fromisoformat(
            "2023-10-30T12:00:00"
        )
        assert pullrequest.first_comment_delay == (1 + (12 - 9)) * 60

    def test_commented_over_weeks(
        self,
        fixture_pull_request_dict,
    ):
        pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
        pullrequest.creation_date = datetime.fromisoformat("2023-10-27T17:00:00")
        pullrequest.comments[0].creation_date = datetime.fromisoformat(
            "2024-01-01T11:00:00"
        )
        pullrequest.comments[1].creation_date = datetime.fromisoformat(
            "2023-11-03T17:00:00"
        )
        # 1 week - 1 day off
        assert pullrequest.first_comment_delay == ((5 - 1) * (18 - 9)) * 60
