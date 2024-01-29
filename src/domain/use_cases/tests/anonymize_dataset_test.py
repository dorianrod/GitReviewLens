import pytest

from src.domain.entities.feature import Feature
from src.domain.entities.pull_request import PullRequest
from src.domain.use_cases.anonymize_dataset import AnonymizeDatasetUseCase


@pytest.fixture
def anonymized_dataset(mock_logger, pull_request, feature):
    transcoder = AnonymizeDatasetUseCase(
        logger=mock_logger,
    )
    return transcoder.execute([pull_request], [feature])


@pytest.fixture
def pull_request(fixture_pull_request_dict):
    return PullRequest.from_dict(fixture_pull_request_dict)


@pytest.fixture
def feature(fixture_feature_dict, pull_request):
    return Feature.from_dict({**fixture_feature_dict, "commit": pull_request.commit})


def test_manage_integrity(mock_logger, pull_request, feature):
    transcoder = AnonymizeDatasetUseCase(
        logger=mock_logger,
    )
    pull_requests, features = transcoder.execute(
        [pull_request, pull_request], [feature, feature]
    )
    assert len(pull_requests) == 2
    assert len(features) == 2

    assert features[0].git_repository == features[1].git_repository
    assert features[0].developer == features[1].developer

    assert pull_requests[0].git_repository == pull_requests[1].git_repository
    assert pull_requests[0].get_developers() == pull_requests[1].get_developers()


def test_filters_out_features_and_pull_requests_before_start_date(
    mock_logger, pull_request, feature
):
    transcoder = AnonymizeDatasetUseCase(
        logger=mock_logger,
    )
    pull_requests, features = transcoder.execute(
        [pull_request], [feature], {"start_date": "2024-10-26T11:10:13"}  # type: ignore
    )
    assert len(pull_requests) == 0
    assert len(features) == 0


def test_filters_out_features_and_pull_requests_after_end_date(
    mock_logger, pull_request, feature
):
    transcoder = AnonymizeDatasetUseCase(
        logger=mock_logger,
    )
    pull_requests, features = transcoder.execute(
        [pull_request], [feature], {"end_date": "2020-10-26T11:10:13"}  # type: ignore
    )
    assert len(pull_requests) == 0
    assert len(features) == 0


def test_anonymize_pull_request_creator(anonymized_dataset, pull_request):
    pull_requests, _ = anonymized_dataset
    assert len(pull_requests) == 1
    assert (
        pull_requests[0].created_by.email
        and pull_requests[0].created_by.email != pull_request.created_by.email
    )
    assert (
        pull_requests[0].created_by.full_name
        and pull_requests[0].created_by.full_name != pull_request.created_by.full_name
    )


def test_anonymize_pull_request_title(anonymized_dataset, pull_request):
    pull_requests, _ = anonymized_dataset
    assert len(pull_requests) == 1
    assert pull_requests[0].title and pull_requests[0].title != pull_request.title


def test_anonymize_pull_request_repository(anonymized_dataset, pull_request):
    pull_requests, _ = anonymized_dataset
    assert len(pull_requests) == 1
    assert pull_requests[0].git_repository.name != pull_request.git_repository.name
    assert (
        pull_requests[0].git_repository.organisation
        != pull_request.git_repository.organisation
    )
    assert (
        pull_requests[0].git_repository.project != pull_request.git_repository.project
    )


def test_anonymize_pull_request_approvers(anonymized_dataset, pull_request):
    pull_requests, _ = anonymized_dataset
    assert len(pull_requests) == 1
    assert len(pull_request.approvers) > 0

    for index, approver in enumerate(pull_request.approvers):
        assert pull_requests[0].approvers[index].email != approver.email
        assert pull_requests[0].approvers[index].full_name != approver.full_name


def test_anonymize_pull_request_commenters(anonymized_dataset, pull_request):
    pull_requests, _ = anonymized_dataset
    assert len(pull_requests) == 1
    assert len(pull_request.comments) > 0

    for index, comment in enumerate(pull_request.comments):
        assert (
            pull_requests[0].comments[index].developer.email != comment.developer.email
        )
        assert (
            pull_requests[0].comments[index].developer.full_name
            != comment.developer.full_name
        )


def test_anonymize_pull_request_comment(anonymized_dataset, pull_request):
    pull_requests, _ = anonymized_dataset
    assert len(pull_request.comments) > 0

    for index, comment in enumerate(pull_request.comments):
        assert pull_requests[0].comments[index].content != comment.content
        assert len(pull_requests[0].comments[index].content) == len(comment.content)


def test_anonymize_feature_developer(anonymized_dataset, feature):
    _, features = anonymized_dataset

    assert len(features) == 1
    assert features[0].developer.full_name != feature.developer.full_name
    assert features[0].developer.email != feature.developer.email


def test_anonymize_feature_repository(anonymized_dataset, feature):
    _, features = anonymized_dataset

    assert len(features) == 1
    assert features[0].git_repository.name != feature.git_repository.name
    assert (
        features[0].git_repository.organisation != feature.git_repository.organisation
    )
    assert features[0].git_repository.project != feature.git_repository.project
