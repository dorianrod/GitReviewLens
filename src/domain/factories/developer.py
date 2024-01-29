from faker import Faker

from src.domain.entities.developer import Developer


class DeveloperFactory:
    @staticmethod
    def create_developer(full_name=None, email=None):
        fake = Faker()
        full_name = full_name or fake.name()
        email = email or fake.email()
        return Developer(full_name=full_name, email=email)
