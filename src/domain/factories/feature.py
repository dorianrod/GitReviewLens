from src.domain.entities.feature import Feature
from src.domain.factories.developer import DeveloperFactory
from src.domain.factories.repository import RepositoryFactory


class FeatureFactory:
    @staticmethod
    def create_feature(
        developer=None, git_repository=None, modified_files=None, **kwargs
    ):
        developer = developer or DeveloperFactory.create_developer()
        git_repository = git_repository or RepositoryFactory.create_repository()
        modified_files = modified_files or []
        return Feature.from_dict(
            {"developer": developer, "git_repository": git_repository, **kwargs}
        )
