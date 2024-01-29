import pytest

from src.domain.entities.developer import Developer
from src.domain.entities.transcoder import Transcoder
from src.domain.use_cases.transcode_developers_in_repository import (
    TranscodeDevelopersInRepositoryUseCase,
)
from src.infra.repositories.in_memory.developers import DevelopersInMemoryRepository


@pytest.fixture
def use_case(mock_logger):
    return TranscodeDevelopersInRepositoryUseCase(
        logger=mock_logger,
        repository=DevelopersInMemoryRepository(logger=mock_logger),
        transcoder=Transcoder("test", {"jean.dujardin@email.com": "JEAN"}),
    )


def test_it_transcodes_developers_in_repository(fixture_developer_dict, use_case):
    original = Developer.from_dict(fixture_developer_dict)
    repository = use_case.repository
    repository.create(original)

    use_case.execute()

    transcoded = repository.get_by_id(original.id)
    assert transcoded.full_name == "JEAN"
    assert original.full_name != transcoded.full_name
