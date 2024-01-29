from dataclasses import dataclass
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.domain.entities.developer import Developer
from src.domain.entities.feature import Feature
from src.domain.entities.repository import Repository
from src.infra.repositories.git.features import FeaturesGit


@pytest.fixture
def features_git():
    return FeaturesGit(MagicMock(), "/path/to/repo")


@pytest.fixture
def commit():
    commit = MagicMock()
    commit.hash = "abcde"
    commit.author = MagicMock()
    commit.project_name = "myrepo"
    commit.committer_date = datetime.fromisoformat("2023-01-02T01:12:17")
    commit.author.name = "John Doe"
    commit.author.email = "john.doe@email.com"
    commit.modified_files = [
        ModifiedFile(
            filename="file1.py",
            new_path="path/to/file1.py",
            deleted_lines=10,
            added_lines=20,
        ),
        ModifiedFile(
            filename="file2.py",
            new_path="path/to/file2.py",
            deleted_lines=5,
            added_lines=15,
        ),
        ModifiedFile(
            filename="test_file.py",
            new_path="path/to/test_file.py",
            deleted_lines=2,
            added_lines=3,
        ),
    ]
    commit.dmm_unit_complexity = 1.0
    commit.dmm_unit_interfacing = 2.0
    commit.dmm_unit_size = 3.0
    return commit


@pytest.fixture
def feature_without_test_files():
    return Feature(
        date=datetime.fromisoformat("2023-01-02T01:12:17"),
        git_repository=Repository.parse("orga/myrepo"),
        count_deleted_lines=15,
        count_inserted_lines=35,
        dmm_unit_complexity=1.0,
        dmm_unit_interfacing=2.0,
        dmm_unit_size=3.0,
        modified_files=[
            "path/to/file1.py",
            "path/to/file2.py",
        ],
        developer=Developer.from_dict(
            {"full_name": "John Doe", "email": "john.doe@email.com"}
        ),
        commit="abcde",
    )


@dataclass
class ModifiedFile:
    filename: str
    new_path: str
    deleted_lines: int
    added_lines: int


def test_get_feature(features_git, mocker, commit, feature_without_test_files):
    mocker.patch(
        "src.infra.repositories.git.features.Git"
    ).return_value.get_commit.return_value = commit
    feature_from_git = features_git.get_by_id("12345", {"exclude_files": "test_.*"})
    assert feature_from_git == feature_without_test_files


def test_find_all(features_git, mocker, commit, feature_without_test_files):
    mocker.patch(
        "src.infra.repositories.git.features.Repository.traverse_commits",
        return_value=[
            MagicMock(hash="abcde"),
        ],
    )
    mocker.patch(
        "src.infra.repositories.git.features.Git"
    ).return_value.get_commit.return_value = commit

    features = features_git.find_all({"exclude_files": "test_.*"})
    assert len(features) == 1

    assert features[0] == feature_without_test_files
