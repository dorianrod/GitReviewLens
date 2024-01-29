import json

from src.settings import settings


def test_get_branches_azure():
    repository_1 = {
        "organisation": "orga",
        "project": "project",
        "url": "git@ssh.dev.azure.com:v3/orga/project/Backend",
        "name": "Backend",
        "token": "azuretoken",
    }

    repository_2 = {
        "organisation": "orga",
        "project": "project",
        "url": "git@ssh.dev.azure.com:v3/orga/project/WebApp",
        "name": "WebApp",
        "token": "azuretoken",
    }

    branch_1 = {
        "name": "master",
        "repository": repository_1,
    }

    branch_2 = {
        "name": "master",
        "repository": repository_2,
    }

    settings.git_branches = json.dumps([branch_1, branch_2])
    repositories = settings.get_branches()
    assert [repositories[0].to_dict(), repositories[1].to_dict()] == [
        branch_1,
        branch_2,
    ]


def test_get_branches_github():
    repository_1 = {
        "organisation": "user",
        "project": "",
        "url": "git@github.com:user/Backend.git",
        "name": "Backend",
        "token": "token",
    }

    repository_2 = {
        "organisation": "user",
        "project": "",
        "url": "git@github.com:user/WebApp.git",
        "name": "WebApp",
        "token": "token",
    }

    branch_1 = {
        "name": "master",
        "repository": repository_1,
    }

    branch_2 = {
        "name": "master",
        "repository": repository_2,
    }

    settings.git_branches = json.dumps([branch_1, branch_2])
    repositories = settings.get_branches()
    assert [repositories[0].to_dict(), repositories[1].to_dict()] == [
        branch_1,
        branch_2,
    ]
