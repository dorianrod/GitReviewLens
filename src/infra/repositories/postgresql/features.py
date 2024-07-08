from sqlalchemy.orm import joinedload

from src.domain.entities.feature import Feature
from src.domain.repositories.features import FeaturesRepository
from src.infra.database.postgresql.database import get_db_session
from src.infra.database.postgresql.models.models import Developer as DeveloperModel
from src.infra.database.postgresql.models.models import Feature as FeatureModel
from src.infra.repositories.postgresql.developers import DeveloperDatabaseRepository
from src.infra.repositories.postgresql.utils import (
    raise_exception_if_upsert_cannot_be_done,
)


class FeaturesDatabaseRepository(FeaturesRepository):
    async def upsert(self, entity, options=None):
        options = options or {}

        await super().upsert(entity, options)

        session = get_db_session()
        feature = (
            session.query(FeatureModel).filter(FeatureModel.id == entity.id).first()
        )
        raise_exception_if_upsert_cannot_be_done(options, feature)

        upsert_developer = options.get("upsert_developer", True)
        if upsert_developer:
            developer_repository = DeveloperDatabaseRepository(logger=self.logger)
            await developer_repository.upsert(entity.developer)

        columns = FeatureModel.from_entity(entity)
        if feature is None:
            self.logger.debug(f"Creating {repr(entity)}")
            feature = FeatureModel(**columns)
        else:
            self.logger.debug(f"Updating {repr(entity)}")
            for key in columns:
                setattr(feature, key, columns[key])

        session.add(feature)
        session.commit()

    async def find_all(self, options=None):
        session = get_db_session()
        results = session.query(FeatureModel).all()

        results = (
            session.query(FeatureModel)
            .options(
                joinedload(FeatureModel.developer),
            )
            .filter(FeatureModel.repository == self.git_repository.path)
            .all()
        )

        features: list[Feature] = []
        for feature in results:
            feature_entity = Feature.from_dict(
                {
                    "id": feature.id,
                    "commit": feature.commit,
                    "count_deleted_lines": feature.count_deleted_lines,
                    "count_inserted_lines": feature.count_inserted_lines,
                    "dmm_unit_complexity": feature.dmm_unit_complexity,
                    "dmm_unit_interfacing": feature.dmm_unit_interfacing,
                    "dmm_unit_size": feature.dmm_unit_size,
                    "date": feature.date,
                    "modified_files": feature.modified_files,
                    "git_repository": feature.repository,
                    "developer": DeveloperModel.to_entity(feature.developer),
                }
            )
            features.append(feature_entity)

        return features
