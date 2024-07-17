from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import text

from src.domain.entities.comment import Comment
from src.domain.entities.feature import Feature
from src.domain.entities.pull_request import PullRequest
from src.infra.database.postgresql.database import get_db_session
from src.infra.repositories.postgresql.features import FeaturesDatabaseRepository
from src.infra.repositories.postgresql.pull_requests import (
    PullRequestsDatabaseRepository,
)


class TestSummaryIndicators:
    async def test_no_filters(self, dataset_1, fetch_all, db_schema):
        query = f"""
            SELECT * from {db_schema}.get_summary_statistics(
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL
            )
        """

        values = await fetch_all(query)

        assert values == [
            {
                'nb_pull_requests': 2,
                'nb_comments_by_pr': 1.0,
                'comments_length_by_pr': 6,
                'merge_time': 300,
                'first_comment_delay': 7.5,
                'count_changed_lines': 4.5,
                'count_delta_changed_lines': 1.5,
            }
        ]


class TestSummaryIndicatorsByWeekday:
    async def test_no_filters(self, dataset_1, fetch_all, db_schema):
        query = f"""
            SELECT *
            FROM {db_schema}.get_summary_statistics_by_week_day(
                'completion',
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL
            )
        """
        values = await fetch_all(query)
        assert values == [
            {
                'week_day': '4-Thu',
                'nb_pull_requests': 1,
                'nb_comments_by_pr': 1.0,
                'comments_length_by_pr': 4,
                'merge_time': 240.0,
                'first_comment_delay': 5.0,
                'count_changed_lines': 3.0,
                'count_delta_changed_lines': 1.0,
            },
            {
                'week_day': '5-Fri',
                'nb_pull_requests': 1,
                'nb_comments_by_pr': 1.0,
                'comments_length_by_pr': 8,
                'merge_time': 360.0,
                'first_comment_delay': 10.0,
                'count_changed_lines': 6.0,
                'count_delta_changed_lines': 2.0,
            },
        ]


expected_1_day = [
    {
        'day': date(2022, 10, 3),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 0.0,
        'comments_length_by_pr': 0,
        'first_comment_delay': None,
        'merge_time': 60.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 4),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 0.0,
        'comments_length_by_pr': 0,
        'first_comment_delay': None,
        'merge_time': 120.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 5),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 0.0,
        'comments_length_by_pr': 0,
        'first_comment_delay': None,
        'merge_time': 180.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 6),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 1.0,
        'comments_length_by_pr': 24,
        'first_comment_delay': 2.0,
        'merge_time': 240.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 7),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 2.0,
        'comments_length_by_pr': 31,
        'first_comment_delay': 5.0,
        'merge_time': 300.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 10),
        'nb_pull_requests': 2.0,
        'nb_comments_by_pr': 1.0,
        'comments_length_by_pr': 16,
        'first_comment_delay': 5.0,
        'merge_time': 360.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 11),
        'nb_pull_requests': 0.0,
        'nb_comments_by_pr': None,
        'comments_length_by_pr': None,
        'first_comment_delay': None,
        'merge_time': None,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
]

expected_2_days = [
    {
        'day': date(2022, 10, 3),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 0.0,
        'comments_length_by_pr': 0,
        'first_comment_delay': None,
        'merge_time': 60.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 4),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 0.0,
        'comments_length_by_pr': 0,
        'first_comment_delay': None,
        'merge_time': 90.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 5),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 0.0,
        'comments_length_by_pr': 0,
        'first_comment_delay': None,
        'merge_time': 150.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 6),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 0.5,
        'comments_length_by_pr': 12,
        'first_comment_delay': 2.0,
        'merge_time': 210.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 7),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 1.5,
        'comments_length_by_pr': 28,
        'first_comment_delay': 3.5,
        'merge_time': 270.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 10),
        'nb_pull_requests': 1.5,
        'nb_comments_by_pr': 2.0,
        'comments_length_by_pr': 31,
        'first_comment_delay': 5.0,
        'merge_time': 360.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
    {
        'day': date(2022, 10, 11),
        'nb_pull_requests': 1.0,
        'nb_comments_by_pr': 1.0,
        'comments_length_by_pr': 16,
        'first_comment_delay': 5.0,
        'merge_time': 360.0,
        'count_changed_lines': None,
        'count_delta_changed_lines': None,
    },
]


class TestSummaryIndicatorsByDay:
    async def test_no_filters(self, dataset_1, fetch_all, db_schema):
        query = f"""
        SELECT *
            FROM {db_schema}.get_summary_statistics_by_day(
                '1 day',
                0.5,
                'completion',
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                '2023-10-26',
                '2023-10-28',
                NULL
            )
        """

        values = await fetch_all(query)

        assert values == [
            {
                'day': date(2023, 10, 26),
                'nb_pull_requests': 1.0,
                'nb_comments_by_pr': 1.0,
                'comments_length_by_pr': 4,
                'first_comment_delay': 5.0,
                'merge_time': 240.0,
                'count_changed_lines': 3.0,
                'count_delta_changed_lines': 1.0,
            },
            {
                'day': date(2023, 10, 27),
                'nb_pull_requests': 1.0,
                'nb_comments_by_pr': 1.0,
                'comments_length_by_pr': 8,
                'first_comment_delay': 10.0,
                'merge_time': 360.0,
                'count_changed_lines': 6.0,
                'count_delta_changed_lines': 2.0,
            },
        ]

    async def test_only_smooth_over_period(self, dataset_1, fetch_all, db_schema):
        query = f"""
        SELECT *
            FROM {db_schema}.get_summary_statistics_by_day(
                '2 day',
                0.5,
                'completion',
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                '2023-10-20',
                '2023-10-28',
                NULL
            )
        """

        values = await fetch_all(query)

        assert values[-2] == {
            'day': date(2023, 10, 26),
            'nb_pull_requests': 0.5,
            'nb_comments_by_pr': 1.0,
            'comments_length_by_pr': 4,
            'first_comment_delay': 5.0,
            'merge_time': 240.0,
            'count_changed_lines': 3.0,
            'count_delta_changed_lines': 1.0,
        }


@pytest.mark.usefixtures("dataset_2")
class TestSummaryIndicatorsByDaySmooth:
    @pytest.mark.parametrize(
        "aggregation_period,expected",
        [
            pytest.param(
                "1 day",
                expected_1_day,
            ),
            pytest.param(
                "2 days",
                expected_2_days,
            ),
        ],
    )
    async def test_smooth_values(
        self, expected, aggregation_period, fetch_all, db_schema
    ):
        query = f"""
            SELECT *
            FROM {db_schema}.get_summary_statistics_by_day(
                '{aggregation_period}',
                0.5,
                'creation',
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                '2022-10-01',
                '2022-10-11',
                NULL
            )
        """

        values = await fetch_all(query)
        assert values == expected


class TestSankeyReviewers:
    async def test_no_filters(
        self, db_schema, dataset_1, pull_request_without_comment, fetch_all
    ):
        query = f"""
            SELECT *
            FROM {db_schema}.get_sankey_reviewers(
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL
            ) AS pr_data
        """
        values = await fetch_all(query)
        assert values == [
            {
                'commenter_name': 'Jean Dujardin',
                'created_by_name': 'Clark Kent',
                'number_comments': 1,
                'number_pr': 1,
            },
            {
                'commenter_name': 'Thomas Dupont',
                'created_by_name': 'Clark Kent',
                'number_comments': 1,
                'number_pr': 1,
            },
        ]


class TestReviewsByTimeranges:
    async def test_no_filters(
        self,
        dataset_1,
        pull_request_without_comment,
        pull_request_with_several_comments,
        fetch_all,
        db_schema,
    ):
        query = f"""
            SELECT *
            FROM {db_schema}.get_review_by_time_ranges(
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL
            ) AS pr_data
        """
        values = await fetch_all(query)

        assert values == [
            {'week_day': '4-Thu', 'time_range': '14:00-14:30', 'count_comments': 1},
            {'week_day': '4-Thu', 'time_range': '13:00-13:30', 'count_comments': 2},
            {'week_day': '5-Fri', 'time_range': '13:00-13:30', 'count_comments': 1},
        ]


class TestMergeTimeByComplexity:
    async def test_no_filters(
        self,
        dataset_1,
        pull_request_without_comment,
        pull_request_with_several_comments,
        fetch_all,
        db_schema,
    ):
        query = f"""
            SELECT *
            FROM {db_schema}.get_merge_time_by_complexity(
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                '7d'
            ) AS pr_data
        """
        values = await fetch_all(query)
        assert values == [
            {
                'pr_id': 'dddb63d29af3496731ef1e3b1f7801c36760800502d1e615e2464fb9c5fac49c',
                'created_by_name': 'Clark Kent',
                'merge_time': 360.0,
                'count_changes': 6,
                'count_changes_delta': 2,
            },
            {
                'pr_id': '8709ea61fd295c6be532a8e6120b1e34ef52904ee031df87e5b30d8046b0edf9',
                'created_by_name': 'Clark Kent',
                'merge_time': 240.0,
                'count_changes': 3,
                'count_changes_delta': 1,
            },
        ]


@pytest.fixture(autouse=True)
def mock_settings(mocker, mock_git_settings):
    mock_git_settings.git_branches = '[{"name":"master","repository":{"organisation":"orga","project":"", "name": "myrepo", "url": "", "token": ""}}]'

    mocker.patch(
        "src.domain.entities.pull_request.settings",
        mock_git_settings,
    )


@pytest.fixture
def fetch_all():
    async def _execute(query):
        async with get_db_session() as session:
            result = await session.execute(text(query))
            rows = result.fetchall()
            keys = result.keys()
            values = [dict(zip(keys, row)) for row in rows]
        return values

    return _execute


@pytest.fixture
async def pull_request_without_comment(
    mock_logger,
    fixture_feature_dict,
    fixture_pull_request_dict,
):
    pull_requests_1 = [
        PullRequest.from_dict(pr)
        for pr in [
            {
                **fixture_pull_request_dict,
                "git_repository": "orga/repo",
                "creation_date": "2023-10-26T11:00:00",
                "completion_date": "2023-10-26T15:00:00",
                "commit": "rep1_no_comment",
                "comments": [],
            },
        ]
    ]

    await PullRequestsDatabaseRepository(
        mock_logger, git_repository="orga/repo"
    ).upsert_all(pull_requests_1)

    features_1 = [
        Feature.from_dict(feature)
        for feature in [
            {
                **fixture_feature_dict,
                "git_repository": "orga/repo",
                "commit": "rep1_no_comment",
            }
        ]
    ]
    await FeaturesDatabaseRepository(
        mock_logger, git_repository="orga/repo"
    ).upsert_all(features_1)


@pytest.fixture
async def pull_request_with_several_comments(
    mock_logger,
    fixture_feature_dict,
    fixture_pull_request_dict,
    fixture_comment_dict,
    fixture_developer_dict,
    fixture_developer_2_dict,
):
    pull_requests_1 = [
        PullRequest.from_dict(pr)
        for pr in [
            {
                **fixture_pull_request_dict,
                "git_repository": "orga/repo",
                "creation_date": "2023-10-19T11:00:00",
                "completion_date": "2023-10-19T15:00:00",
                "commit": "rep1_several_comments",
                "comments": [
                    {
                        **fixture_comment_dict,
                        "developer": fixture_developer_dict,
                        "content": "test",
                        "creation_date": "2023-10-19T12:00:00",
                    },
                    {
                        **fixture_comment_dict,
                        "developer": fixture_developer_2_dict,
                        "content": "anothertest",
                        "creation_date": "2023-10-19T11:10:00",
                    },
                ],
            },
        ]
    ]

    await PullRequestsDatabaseRepository(
        mock_logger, git_repository="orga/repo"
    ).upsert_all(pull_requests_1)

    features_1 = [
        Feature.from_dict(feature)
        for feature in [
            {
                **fixture_feature_dict,
                "git_repository": "orga/repo",
                "commit": "rep1_several_comments",
            }
        ]
    ]
    await FeaturesDatabaseRepository(
        mock_logger, git_repository="orga/repo"
    ).upsert_all(features_1)


@pytest.fixture
async def dataset_1(
    mock_logger,
    fixture_feature_dict,
    fixture_pull_request_dict,
    fixture_developer_dict,
    fixture_developer_2_dict,
    fixture_comment_dict,
):
    pull_requests_1 = [
        PullRequest.from_dict(pr)
        for pr in [
            {
                **fixture_pull_request_dict,
                "git_repository": "orga/repo",
                "creation_date": "2023-10-26T11:00:00",
                "completion_date": "2023-10-26T15:00:00",
                "commit": "rep1_1",
                "comments": [
                    {
                        **fixture_comment_dict,
                        "developer": fixture_developer_dict,
                        "content": "test",
                        "creation_date": "2023-10-26T11:05:00",
                    }
                ],
            },
        ]
    ]

    await PullRequestsDatabaseRepository(
        mock_logger, git_repository="orga/repo"
    ).create_all(pull_requests_1)

    features_1 = [
        Feature.from_dict(feature)
        for feature in [
            {
                **fixture_feature_dict,
                "git_repository": "orga/repo",
                "commit": "rep1_1",
            }
        ]
    ]
    await FeaturesDatabaseRepository(
        mock_logger, git_repository="orga/repo"
    ).create_all(features_1)

    pull_requests_2 = [
        PullRequest.from_dict(pr)
        for pr in [
            {
                **fixture_pull_request_dict,
                "git_repository": "orga/anotherrepo",
                "creation_date": "2023-10-27T11:00:00",
                "completion_date": "2023-10-27T17:00:00",
                "commit": "rep2_1",
                "comments": [
                    {
                        **fixture_comment_dict,
                        "developer": fixture_developer_2_dict,
                        "content": "testtoto",
                        "creation_date": "2023-10-27T11:10:00",
                    }
                ],
            },
        ]
    ]
    await PullRequestsDatabaseRepository(
        mock_logger, git_repository="orga/anotherrepo"
    ).create_all(pull_requests_2)

    features_2 = [
        Feature.from_dict(feature)
        for feature in [
            {
                **fixture_feature_dict,
                "git_repository": "orga/anotherrepo",
                "commit": "rep2_1",
                "count_deleted_lines": 2,
                "count_inserted_lines": 4,
            }
        ]
    ]
    await FeaturesDatabaseRepository(
        mock_logger, git_repository="orga/anotherrepo"
    ).create_all(features_2)


@pytest.fixture
async def dataset_2(
    mock_logger,
    fixture_comment_dict,
    fixture_pull_request_dict,
):
    pull_requests = []

    # 5 business days + excluded weekend + 1 business day next week
    for i in range(0, 6):
        creation_date = datetime.strptime(
            "2022-10-03T11:10:13", "%Y-%m-%dT%H:%M:%S"
        ) + timedelta(days=i + (0 if i <= 4 else 2))

        completion_date = creation_date + timedelta(hours=1 + i)

        pr_1 = PullRequest.from_dict(
            {
                **fixture_pull_request_dict,
                "source_id": str(i),
                "git_repository": "orga/repo",
                "comments": [],
                "creation_date": creation_date.isoformat(),
                "completion_date": completion_date.isoformat(),
            }
        )

        if i >= 3:
            comment_date = creation_date + timedelta(minutes=2 if i == 3 else 5)
            pr_1.comments.append(
                Comment.from_dict(
                    {
                        **fixture_comment_dict,
                        "creation_date": comment_date.isoformat(),
                    }
                )
            )

        if i >= 4:
            comment_date = creation_date + timedelta(minutes=3 if i == 3 else 6)
            pr_1.comments.append(
                Comment.from_dict(
                    {
                        **fixture_comment_dict,
                        "content": "another",
                        "creation_date": comment_date.isoformat(),
                    }
                )
            )

        if i == 5:
            pr_2 = PullRequest.from_dict(
                {
                    **fixture_pull_request_dict,
                    "source_id": str(i) + "_2",
                    "git_repository": "orga/repo",
                    "comments": [],
                    "creation_date": creation_date.isoformat(),
                    "completion_date": completion_date.isoformat(),
                }
            )
            pull_requests.append(pr_2)

        pull_requests.append(pr_1)

    await PullRequestsDatabaseRepository(
        mock_logger, git_repository="orga/repo"
    ).upsert_all(pull_requests)
