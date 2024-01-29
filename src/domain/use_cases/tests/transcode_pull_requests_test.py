from src.domain.entities.pull_request import PullRequest
from src.domain.entities.transcoder import Transcoder
from src.domain.use_cases.transcode_pull_requests import TranscodePullRequestsUseCase


def test_transcode_pull_requests_type(fixture_pull_request_dict, mock_logger):
    pullrequest = PullRequest.from_dict(fixture_pull_request_dict)
    transcoder = TranscodePullRequestsUseCase(
        logger=mock_logger,
        transcoder=Transcoder(
            "pull_requests_type", {"feat": "coolfeature", "": "other"}
        ),
    )
    pullrequests = transcoder.execute([pullrequest])
    assert pullrequests[0].type == "coolfeature"
