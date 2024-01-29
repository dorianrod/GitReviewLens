from faker import Faker

from src.common.utils.string import clean_string
from src.domain.entities.repository import Repository


class RepositoryFactory:
    @staticmethod
    def create_repository(organisation=None, project=None, name=None, url="", token=""):
        fake = Faker()

        organisation = organisation or clean_string(fake.company_suffix())
        project = project or clean_string(fake.company_suffix())
        name = name or clean_string(fake.last_name_nonbinary())

        return Repository(
            name=name, organisation=organisation, project=project, url=url, token=token
        )
