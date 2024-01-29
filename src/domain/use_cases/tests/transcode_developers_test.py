from src.domain.entities.developer import Developer
from src.domain.entities.transcoder import Transcoder
from src.domain.use_cases.transcode_developers import TranscodeDevelopersUseCase


def test_transcode_developer_name(fixture_developer_dict, mock_logger):
    developer = Developer.from_dict(fixture_developer_dict)
    transcoder = TranscodeDevelopersUseCase(
        transcoder=Transcoder(
            "developers_name",
            {
                "jean.dujardin@email.com": "JEAN",
                "thomas.dupont@email.com": "TOM",
                "clark.kent@email.com": "CLARK",
            },
        ),
        logger=mock_logger,
    )
    developers = transcoder.execute([developer])
    assert developers[0].full_name == "JEAN"
