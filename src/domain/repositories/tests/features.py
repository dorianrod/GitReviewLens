import pytest

from src.domain.entities.feature import Feature
from src.domain.exceptions import RepositoryIncompatibility


def test_upsert(feature_repository, fixture_feature_dict):
    feature = Feature.from_dict(fixture_feature_dict)
    feature_repository.upsert(feature)
    assert feature_repository.find_all() == [feature]


def test_cannot_create_into_wrong_git_repo(feature_repository, fixture_feature_dict):
    feature = Feature.from_dict(
        {**fixture_feature_dict, "git_repository": "orga/another_repo"}
    )
    with pytest.raises(RepositoryIncompatibility):
        feature_repository.create(feature)

    assert feature_repository.find_all() == []


def test_create_same_id_in_two_repos(
    feature_repository, feature_repository_2, fixture_feature_dict
):
    feature = Feature.from_dict(fixture_feature_dict)
    feature_repository.create(feature)

    feature_2 = Feature.from_dict(
        {**fixture_feature_dict, "git_repository": feature_repository_2.git_repository}
    )
    feature_repository_2.create(feature_2)

    assert feature_repository.find_all() == [feature]
    assert feature_repository_2.find_all() == [feature_2]


def test_update(feature_repository, fixture_feature_dict):
    feature = Feature.from_dict(fixture_feature_dict)
    feature_repository.create(feature)

    feature.count_deleted_lines = 10000
    feature_repository.update(feature)

    assert feature_repository.find_all() == [feature]


def test_upsert_all(feature_repository, fixture_feature_dict):
    feature = Feature.from_dict(fixture_feature_dict)
    feature_repository.upsert_all([feature])

    assert feature_repository.find_all() == [feature]


def test_find_all(feature_repository, fixture_feature_dict):
    feature = Feature.from_dict(fixture_feature_dict)
    feature_repository.create(feature)

    assert feature_repository.find_all() == [feature]


def test_find_all_does_not_return_features_from_other_repositories(
    feature_repository, feature_repository_2, fixture_feature_dict
):
    feature = Feature.from_dict(fixture_feature_dict)
    feature_repository.create(feature)

    result = feature_repository_2.find_all()
    assert len(result) == 0
