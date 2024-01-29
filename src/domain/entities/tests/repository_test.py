import pytest

from src.domain.entities.repository import Repository
from src.domain.entities.types import RepositoryTypes


class TestGithub:
    @pytest.mark.parametrize(
        "source",
        [
            "user/myrepo",
            "user/myrepo:",
            {
                "name": "myrepo",
                "organisation": "user",
            },
            {
                "name": "myrepo",
                "project": "user",
            },
            Repository(
                project=None,
                organisation="user",
                name="myrepo",
                url=None,
            ),
            Repository(
                project="user",
                organisation=None,
                name="myrepo",
                url=None,
            ),
        ],
    )
    def test_parse_string_without_url(self, source):
        repository = Repository.parse(source)
        assert repository.path == "user/myrepo"
        assert str(repository) == "user/myrepo"
        assert repository.organisation == "user" or repository.project == "user"
        assert repository.name == "myrepo"

    @pytest.mark.parametrize(
        "source",
        [
            "user/myrepo:git@github.com:user/myrepo.git",
            {
                "name": "myrepo",
                "organisation": "user",
                "url": "git@github.com:user/myrepo.git",
            },
            {
                "name": "myrepo",
                "project": "user",
                "url": "git@github.com:user/myrepo.git",
            },
            Repository(
                project=None,
                organisation="user",
                name="myrepo",
                url="git@github.com:user/myrepo.git",
            ),
            Repository(
                project="user",
                organisation=None,
                name="myrepo",
                url="git@github.com:user/myrepo.git",
            ),
        ],
    )
    def test_parse_string_with_url(self, source):
        repository = Repository.parse(source)
        assert repository.path == "user/myrepo"
        assert str(repository) == "user/myrepo"
        assert repository.organisation == "user" or repository.project == "user"
        assert repository.name == "myrepo"
        assert repository.url == "git@github.com:user/myrepo.git"

    def test_repository_type(self):
        repository = Repository.parse(
            {
                "url": "git@github.com:user/myrepo.git",
                "organisation": "",
                "project": "",
                "name": "",
            }
        )
        assert repository.type == RepositoryTypes.GITHUB


class TestAzure:
    @pytest.mark.parametrize(
        "source",
        [
            "orga/project/Backend",
            "orga/project/Backend:",
            {
                "name": "Backend",
                "project": "project",
                "organisation": "orga",
            },
            Repository(
                organisation="orga",
                project="project",
                name="Backend",
                url=None,
            ),
        ],
    )
    def test_parse_string_without_url(self, source):
        repository = Repository.parse(source)
        assert repository.path == "orga/project/Backend"
        assert str(repository) == "orga/project/Backend"
        assert repository.organisation == "orga"
        assert repository.project == "project"
        assert repository.name == "Backend"

    @pytest.mark.parametrize(
        "source",
        [
            "orga/project/Backend:git@ssh.dev.azure.com:v3/orga/project/Backend",
            {
                "name": "Backend",
                "project": "project",
                "organisation": "orga",
                "url": "git@ssh.dev.azure.com:v3/orga/project/Backend",
            },
            Repository(
                organisation="orga",
                project="project",
                name="Backend",
                url="git@ssh.dev.azure.com:v3/orga/project/Backend",
            ),
        ],
    )
    def test_parse_string_with_url(self, source):
        repository = Repository.parse(source)
        assert repository.path == "orga/project/Backend"
        assert str(repository) == "orga/project/Backend"
        assert repository.organisation == "orga"
        assert repository.project == "project"
        assert repository.name == "Backend"
        assert repository.url == "git@ssh.dev.azure.com:v3/orga/project/Backend"

    def test_repository_type(self):
        repository = Repository.parse(
            {
                "url": "git@ssh.dev.azure.com:v3/orga/project/Backend",
                "organisation": "",
                "project": "",
                "name": "",
            }
        )
        assert repository.type == RepositoryTypes.AZURE
