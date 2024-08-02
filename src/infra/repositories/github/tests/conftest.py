import pytest


@pytest.fixture
def mock_api_comments(mocker_aio):
    def mock(pr_id, payload, per_page=100, page=1):
        mocker_aio.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pr_id}/comments?per_page={per_page}&page={page}",
            payload=payload,
        )

    return mock


@pytest.fixture
def mock_api_approvers(mocker_aio):

    def mock(pr_id, payload=[], per_page=100, page=1, status=200):
        mocker_aio.get(
            f"https://api.github.com/repos/orga/myrepo/pulls/{pr_id}/reviews?per_page={per_page}&page={page}",
            payload=payload,
            status=status,
        )

    return mock


@pytest.fixture
def mock_api_pull_requests(mocker_aio):
    def mock(payload, per_page=100, page=1):
        mocker_aio.get(
            f"https://api.github.com/repos/orga/myrepo/pulls?state=closed&per_page={per_page}&page={page}",
            payload=payload,
        )

    return mock


@pytest.fixture
def mock_active_pull_request_in_github():
    return {
        "number": 1347,
        "state": "open",
        "title": "Amazing new feature",
        "user": {"login": "octocat", "id": 1, "type": "User"},
        "active_lock_reason": "too heated",
        "created_at": "2011-01-26T12:01:12Z",
        "updated_at": "2011-01-26T12:02:12Z",
        "closed_at": "2011-01-26T12:03:12Z",
        "merged_at": "2011-01-26T12:03:12Z",
        "merge_commit_sha": "e5bd3914e2e596debea16f433f57875b5b90bcd6",
        "head": {
            "ref": "new-topic",
            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            "user": {"login": "octocat", "id": 1},
        },
        "base": {
            "ref": "master",
            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            "user": {
                "login": "octocat",
                "id": 1,
            },
        },
    }


@pytest.fixture
def mock_completed_pull_request_in_github(mock_active_pull_request_in_github):
    return {
        **mock_active_pull_request_in_github,
        "state": "closed",
        "number": 1234,
    }


@pytest.fixture
def mock_approver_in_github():
    return {
        "user": {"login": "approveruser", "id": 12, "type": "User"},
        "state": "APPROVED",
    }


@pytest.fixture
def mock_approver_2_in_github():
    return {
        "user": {"login": "anotherapprover", "id": 3535, "type": "User"},
        "state": "APPROVED",
    }


@pytest.fixture
def mock_commenter_in_github():
    return {
        "user": {"login": "dupond", "id": 124, "type": "User"},
        "state": "COMMENTED",
    }


@pytest.fixture
def mock_approvers_in_github(mock_approver_in_github, mock_commenter_in_github):
    return [mock_approver_in_github, mock_commenter_in_github]


@pytest.fixture
def mock_completed_pull_request_2_in_github(
    mock_completed_pull_request_in_github,
):
    return {**mock_completed_pull_request_in_github, "number": 789}


@pytest.fixture
def mock_pull_request_user_comment_in_github():
    return {
        "id": 10,
        "node_id": "MDI0OlB1bGxSZXF1ZXN0UmV2aWV3Q29tbWVudDEw",
        "diff_hunk": "@@ -16,33 +16,40 @@ public class Connection : IConnection...",
        "path": "file1.txt",
        "position": 1,
        "original_position": 4,
        "commit_id": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
        "original_commit_id": "9c48853fa3dc5c1c3d6f1f1cd1f2743e72652840",
        "user": {
            "login": "octocat",
            "id": 1,
            "type": "User",
        },
        "body": "Great stuff!",
        "created_at": "2011-04-14T16:00:49Z",
        "updated_at": "2011-04-14T16:00:50Z",
    }


@pytest.fixture
def mock_pull_request_user_comment_2_in_github(
    mock_pull_request_user_comment_in_github,
):
    return {
        **mock_pull_request_user_comment_in_github,
        "user": {
            "login": "dupont",
            "id": 2,
            "type": "User",
        },
        "body": "Yes!",
        "created_at": "2012-04-14T16:00:49Z",
        "updated_at": "2012-04-14T16:00:49Z",
    }
