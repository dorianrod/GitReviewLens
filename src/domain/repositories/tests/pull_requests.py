import pytest

from src.domain.entities.pull_request import PullRequest
from src.domain.exceptions import NotExistsException, RepositoryIncompatibility


def test_upsert(pull_request_repository, fixture_pull_request_dict):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request_repository.upsert(pull_request)
    assert pull_request_repository.find_all() == [pull_request]


def test_cannot_create_into_wrong_git_repo(
    pull_request_repository_2, fixture_pull_request_dict
):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    with pytest.raises(RepositoryIncompatibility):
        pull_request_repository_2.create(pull_request)

    assert pull_request_repository_2.find_all() == []


def test_create_same_id_in_two_repos(
    pull_request_repository, pull_request_repository_2, fixture_pull_request_dict
):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request_repository.create(pull_request)

    pull_request_2 = PullRequest.from_dict(
        {
            **fixture_pull_request_dict,
            "git_repository": pull_request_repository_2.git_repository,
        }
    )
    pull_request_repository_2.create(pull_request_2)

    assert pull_request_repository.find_all() == [pull_request]
    assert pull_request_repository_2.find_all() == [pull_request_2]


def test_update(pull_request_repository, fixture_pull_request_dict):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request_repository.create(pull_request)
    pull_request.title = "my hotfix"
    pull_request_repository.update(pull_request, {"upsert_comments": False})

    assert pull_request_repository.find_all() == [pull_request]

    expected_pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    expected_pull_request.title = "my hotfix"

    assert pull_request_repository.find_all() == [expected_pull_request]


def test_upsert_all(pull_request_repository, fixture_pull_request_dict):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request_repository.upsert_all([pull_request])

    assert pull_request_repository.find_all() == [pull_request]


def test_find_all(
    pull_request_repository,
    fixture_pull_request_dict,
):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request_repository.create(pull_request)
    assert pull_request_repository.find_all() == [pull_request]


def test_find_all_does_not_return_pull_requests_from_other_repositories(
    pull_request_repository,
    pull_request_repository_2,
    fixture_pull_request_dict,
):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request_repository.create(pull_request)

    assert pull_request_repository_2.find_all() == []


def test_get_by_id(
    pull_request_repository,
    fixture_pull_request_dict,
):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request_repository.create(pull_request)

    assert pull_request_repository.get_by_id(pull_request.id) == pull_request


def test_get_by_id_does_not_return_pull_requests_from_other_repositories(
    pull_request_repository,
    pull_request_repository_2,
    fixture_pull_request_dict,
):
    pull_request = PullRequest.from_dict(fixture_pull_request_dict)
    pull_request_repository.create(pull_request)

    with pytest.raises(NotExistsException):
        pull_request_repository_2.get_by_id(pull_request.id)
