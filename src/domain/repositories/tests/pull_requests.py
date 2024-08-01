import pytest

from src.domain.entities.pull_request import PullRequest
from src.domain.exceptions import NotExistsException, RepositoryIncompatibility


def assert_equal_dict(pr1, pr2):
    assert pr1 == pr2


class MixinPullRequests:
    async def test_upsert(self, pull_request_repository, fixture_pull_request_dict):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        await pull_request_repository.upsert(pull_request)
        all_pr = await pull_request_repository.find_all()
        assert_equal_dict(all_pr[0], pull_request)

    async def test_cannot_create_into_wrong_git_repo(
        self, pull_request_repository_2, fixture_pull_request_dict
    ):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        with pytest.raises(RepositoryIncompatibility):
            await pull_request_repository_2.create(pull_request)

        assert await pull_request_repository_2.find_all() == []

    async def test_create_same_id_in_two_repos(
        self,
        pull_request_repository,
        pull_request_repository_2,
        fixture_pull_request_dict,
    ):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        await pull_request_repository.create(pull_request)

        pull_request_2 = PullRequest.from_dict(
            {
                **fixture_pull_request_dict,
                "git_repository": pull_request_repository_2.git_repository,
            }
        )
        await pull_request_repository_2.create(pull_request_2)

        all_pr = await pull_request_repository.find_all()
        assert_equal_dict(all_pr[0], pull_request)

        all_pr_2 = await pull_request_repository_2.find_all()
        assert_equal_dict(all_pr_2[0], pull_request_2)

    async def test_update(self, pull_request_repository, fixture_pull_request_dict):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        await pull_request_repository.create(pull_request)
        pull_request.title = "my hotfix"
        await pull_request_repository.update(pull_request, {"upsert_comments": False})

        all_pr = await pull_request_repository.find_all()
        assert_equal_dict(all_pr[0], pull_request)

        expected_pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        expected_pull_request.title = "my hotfix"

        all_pr = await pull_request_repository.find_all()
        assert_equal_dict(all_pr[0], pull_request)

    async def test_upsert_all(self, pull_request_repository, fixture_pull_request_dict):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        await pull_request_repository.upsert_all([pull_request])

        all_pr = await pull_request_repository.find_all()
        assert_equal_dict(all_pr[0], pull_request)

    async def test_find_all(
        self,
        pull_request_repository,
        fixture_pull_request_dict,
    ):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        await pull_request_repository.create(pull_request)
        all_pr = await pull_request_repository.find_all()
        assert_equal_dict(all_pr[0], pull_request)

    async def test_find_all_does_not_return_pull_requests_from_other_repositories(
        self,
        pull_request_repository,
        pull_request_repository_2,
        fixture_pull_request_dict,
    ):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        await pull_request_repository.create(pull_request)

        assert await pull_request_repository_2.find_all() == []

    async def test_get_by_id(
        self,
        pull_request_repository,
        fixture_pull_request_dict,
    ):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        await pull_request_repository.create(pull_request)

        pr = await pull_request_repository.get_by_id(pull_request.id)
        assert_equal_dict(pr, pull_request)

    async def test_get_by_id_does_not_return_pull_requests_from_other_repositories(
        self,
        pull_request_repository,
        pull_request_repository_2,
        fixture_pull_request_dict,
    ):
        pull_request = PullRequest.from_dict(fixture_pull_request_dict)
        await pull_request_repository.create(pull_request)

        with pytest.raises(NotExistsException):
            await pull_request_repository_2.get_by_id(pull_request.id)
