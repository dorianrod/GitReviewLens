from datetime import datetime

from src.common.utils.date import parse_date
from src.domain.entities.developer import Developer
from src.domain.entities.repository import Repository

from ..feature import Feature


def test_feature_creation(fixture_developer_dict):
    feature = Feature(
        commit="123",
        git_repository=Repository.parse("orga/myrepo"),
        date=datetime.fromisoformat("2023-01-02T01:12:17"),
        developer=Developer.from_dict(fixture_developer_dict),
        count_deleted_lines=1,
        count_inserted_lines=2,
        dmm_unit_complexity=0.5,
        dmm_unit_interfacing=0.6,
        dmm_unit_size=120,
        modified_files=["path/to/feature", "otherpath/to/anotherfeature"],
    )
    assert feature.git_repository.path == "orga/myrepo"
    assert feature.commit == "123"
    assert feature.count_deleted_lines == 1
    assert feature.count_inserted_lines == 2
    assert feature.dmm_unit_complexity == 0.5
    assert feature.dmm_unit_interfacing == 0.6
    assert feature.dmm_unit_size == 120
    assert feature.developer == Developer.from_dict(fixture_developer_dict)
    assert feature.date == parse_date("2023-01-02T01:12:17")
    assert feature.modified_files == [
        "path/to/feature",
        "otherpath/to/anotherfeature",
    ]


def test_feature_from_dict(
    fixture_feature_dict,
):
    feature = Feature.from_dict(fixture_feature_dict)
    to_dict = feature.to_dict()

    assert {
        **fixture_feature_dict,
        "date": "2023-01-02T01:12:17Z",
        "developer": feature.developer.to_dict(),
        "count_modified_lines": 3,
        "count_modified_files": 2,
    } == to_dict


def test_feature_to_dict(fixture_feature_dict):
    feature = Feature(
        git_repository=Repository.parse("orga/myrepo"),
        commit="123",
        count_deleted_lines=1,
        count_inserted_lines=2,
        dmm_unit_complexity=0.5,
        dmm_unit_interfacing=0.6,
        dmm_unit_size=120,
        date=datetime.fromisoformat("2023-01-02T01:12:17"),
        modified_files=["path/to/feature", "otherpath/to/anotherfeature"],
        developer=Developer.from_dict(fixture_feature_dict["developer"]),
    )

    assert {
        **fixture_feature_dict,
        "date": "2023-01-02T01:12:17Z",
        "developer": feature.developer.to_dict(),
        "count_modified_lines": 3,
        "count_modified_files": 2,
    } == feature.to_dict()


def test_feature_comparison(fixture_feature_dict):
    feature_1 = Feature.from_dict(fixture_feature_dict)
    feature_2 = Feature.from_dict(fixture_feature_dict)
    feature_3 = Feature.from_dict(fixture_feature_dict)
    feature_3.commit = "other_commit"
    assert feature_1 == feature_2
    assert feature_1 != feature_3
