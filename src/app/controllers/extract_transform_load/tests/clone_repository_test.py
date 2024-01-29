from unittest.mock import patch

import pytest

from src.app.controllers.extract_transform_load.clone_repository import (
    CloneRepositoriesController,
)
from src.infra.repositories.git.repositories import GitRepoLocal


@pytest.fixture(scope="function", autouse=True)
def mock_settings(mocker, mock_git_settings):
    mocker.patch(
        "src.app.controllers.extract_transform_load.clone_repository.settings",
        mock_git_settings,
    )


def test_call_use_case_for_each_repo(mock_logger, mock_git_settings):
    with patch.object(
        GitRepoLocal,
        'clone',
        return_value=[],
    ) as mock:
        controller = CloneRepositoriesController(logger=mock_logger)
        controller.execute()

        branches = mock_git_settings.get_branches()

        assert mock.call_count == len(branches)

        repo_1 = branches[0].repository
        assert mock.call_args_list[0].args == (
            repo_1.url,
            repo_1.name,
        )
        repo_2 = branches[1].repository
        assert mock.call_args_list[1].args == (
            repo_2.url,
            repo_2.name,
        )
