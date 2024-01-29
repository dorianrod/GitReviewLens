import pytest

from src.domain.entities.branch import Branch
from src.domain.entities.repository import Repository


class TestGithub:
    @pytest.mark.parametrize(
        "source",
        [
            "user/myrepo:master",
            "user/myrepo::master",
            {
                "name": "master",
                "repository": "user/myrepo",
            },
            Branch(
                repository=Repository(
                    project="user", organisation=None, name="myrepo", url=None
                ),
                name="master",
            ),
        ],
    )
    def test_parse_string_without_url(self, source):
        branch = Branch.parse(source)
        assert branch.repository.path == "user/myrepo"
        assert branch.name == "master"

    @pytest.mark.parametrize(
        "source",
        [
            "user/myrepo:git@github.com:user/myrepo.git:master",
            {
                "name": "master",
                "repository": "user/myrepo:git@github.com:user/myrepo.git",
            },
            Branch(
                repository=Repository(
                    project="user",
                    organisation=None,
                    name="myrepo",
                    url="git@github.com:user/myrepo.git",
                ),
                name="master",
            ),
        ],
    )
    def test_parse_string_with_url(self, source):
        branch = Branch.parse(source)
        assert branch.repository.path == "user/myrepo"
        assert branch.repository.url == "git@github.com:user/myrepo.git"
        assert branch.name == "master"


class TestAzure:
    @pytest.mark.parametrize(
        "source",
        [
            "orga/project/Backend:master",
            "orga/project/Backend::master",
            {
                "name": "master",
                "repository": "orga/project/Backend",
            },
            Branch(
                repository=Repository(
                    organisation="orga",
                    project="project",
                    name="Backend",
                    url=None,
                ),
                name="master",
            ),
        ],
    )
    def test_parse_string_without_url(self, source):
        branch = Branch.parse(source)
        assert branch.repository.path == "orga/project/Backend"
        assert branch.name == "master"

    @pytest.mark.parametrize(
        "source",
        [
            "orga/project/Backend:git@ssh.dev.azure.com:v3/orga/project/Backend:master",
            {
                "name": "master",
                "repository": "orga/project/Backend:git@ssh.dev.azure.com:v3/orga/project/Backend",
            },
            Branch(
                repository=Repository(
                    organisation="orga",
                    project="project",
                    name="Backend",
                    url="git@ssh.dev.azure.com:v3/orga/project/Backend",
                ),
                name="master",
            ),
        ],
    )
    def test_parse_string_with_url(self, source):
        branch = Branch.parse(source)
        assert branch.repository.path == "orga/project/Backend"
        assert branch.repository.url == "git@ssh.dev.azure.com:v3/orga/project/Backend"
        assert branch.name == "master"
