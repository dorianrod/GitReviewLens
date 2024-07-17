import pytest


@pytest.fixture
def mock_thread_comments():
    def mock(mocker, pull_request_id, comments):
        mocker.get(
            f"https://dev.azure.com/orga/testproject/_apis/git/repositories/myrepo/pullRequests/{pull_request_id}/threads",
            payload={
                "value": comments,
            },
        )

    return mock


@pytest.fixture
def mock_active_pull_request_in_azure():
    return {
        "pullRequestId": 1,
        "status": "active",
        "createdBy": {
            "displayName": "Developer 1",
            "id": "1",
            "uniqueName": "developer1@org.com",
        },
        "creationDate": "2023-10-16T17:14:08.5301728Z",
        "title": "feat: top feature",
        "reviewers": [],
        "sourceRefName": "feat/add-button",
    }


@pytest.fixture
def mock_completed_pull_request_in_azure():
    return {
        "pullRequestId": 2,
        "status": "completed",
        "createdBy": {
            "displayName": "Developer 1",
            "id": "1",
            "uniqueName": "developer1@org.com",
        },
        "creationDate": "2023-10-16T17:14:08.5301728Z",
        "closedDate": "2023-10-17T17:14:08.5301728Z",
        "title": "fix: ultra priority",
        "sourceRefName": "feat/add-button",
        "targetRefName": "master",
        "lastMergeTargetCommit": {
            "commitId": "129d8cc954433cd62789076de4068701d54ce8ee",
        },
        "lastMergeSourceCommit": {
            "commitId": "8404787b56000382efe2470506c9d3d174ae306c",
        },
        "reviewers": [
            {
                "displayName": "Developer 2",
                "id": "2",
                "uniqueName": "developer2@org.com",
                "vote": 10,
            },
            {
                "displayName": "Developer 3",
                "id": "3",
                "uniqueName": "developer3@org.com",
                "vote": 15,
            },
        ],
    }


@pytest.fixture
def mock_completed_pull_request_2_in_azure(
    mock_completed_pull_request_in_azure,
):
    return {**mock_completed_pull_request_in_azure, "pullRequestId": 3}


def mock_pull_request_comments_thread(comments):
    return {
        "id": 1,
        "publishedDate": "2023-10-09T12:04:49.927Z",
        "lastUpdatedDate": "2023-10-09T12:04:49.927Z",
        "comments": comments,
    }


@pytest.fixture
def mock_pull_request_system_comment():
    return {
        "id": 1,
        "parentCommentId": 0,
        "author": {
            "displayName": "Microsoft.VisualStudio.Services.TFS",
        },
        "content": "Toto set auto-complete",
        "publishedDate": "2023-10-09T12:04:49.927Z",
        "lastUpdatedDate": "2023-10-09T12:04:49.927Z",
        "lastContentUpdatedDate": "2023-10-09T12:04:49.927Z",
        "commentType": "system",
    }


@pytest.fixture
def mock_pull_request_user_comment():
    return {
        "id": 1,
        "parentCommentId": 0,
        "author": {
            "displayName": "Dorian RODRIGUEZ",
            "uniqueName": "dorian.rodriguez@email.com",
        },
        "content": "This is my first comment",
        "publishedDate": "2023-10-09T12:04:49.927Z",
        "lastUpdatedDate": "2023-10-09T12:04:49.927Z",
        "lastContentUpdatedDate": "2023-10-09T12:04:49.927Z",
        "commentType": "text",
    }


@pytest.fixture
def mock_pull_request_user_2_comment():
    return {
        "id": 2,
        "parentCommentId": 0,
        "author": {
            "displayName": "Juan DOMINGO",
            "uniqueName": "juan.domingo@email.com",
        },
        "content": "OK",
        "publishedDate": "2024-10-09T12:04:49.927Z",
        "lastUpdatedDate": "2024-10-09T12:05:49.927Z",
        "lastContentUpdatedDate": "2023-10-09T12:08:49.927Z",
        "commentType": "text",
    }
