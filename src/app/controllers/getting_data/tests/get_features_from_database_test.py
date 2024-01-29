from src.app.controllers.getting_data.get_features_from_database import (
    GetFeaturesController,
)
from src.domain.entities.feature import Feature
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository


def test_get_features(mock_logger, fixture_feature_dict):
    controller = GetFeaturesController(
        logger=mock_logger, git_repository="orga/project/Backend"
    )
    db_repo = FeaturesDatabaseRepository(
        logger=mock_logger, git_repository="orga/project/Backend"
    )

    feature = Feature.from_dict(
        {**fixture_feature_dict, "git_repository": "orga/project/Backend"}
    )
    db_repo.upsert(
        Feature.from_dict(
            {**fixture_feature_dict, "git_repository": "orga/project/Backend"}
        )
    )

    assert controller.execute() == [feature]
