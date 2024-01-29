from datetime import datetime

import pytest
import pytz

from src.common.utils.date import (
    date_to_iso,
    extract_hours_and_minutes,
    get_business_time_diff,
    parse_date,
)


@pytest.mark.parametrize(
    "date,expected",
    [
        ("2023-10-27T11:10:22", "2023-10-27T11:10:22+00:00"),
        ("2023-10-27T11:10:22Z", "2023-10-27T11:10:22+00:00"),
        ("2023-10-27T10:10:22+02:00", "2023-10-27T10:10:22+02:00"),
        ("1699625153", "2023-11-10T14:05:53+00:00"),
        ("1699625153400", "2023-11-10T14:05:53.400000+00:00"),
        ("2023-11-10T15:05:53.400000", "2023-11-10T15:05:53.400000+00:00"),
        ("2023-11-10T15:05:53.400000Z", "2023-11-10T15:05:53.400000+00:00"),
        ("2023-10-27", "2023-10-27T00:00:00+00:00"),
    ],
)
def test_parse_date(date, expected):
    assert parse_date(date).isoformat() == expected


@pytest.mark.parametrize(
    "date,expected",
    [
        ("2023-10-27T11:10:22", "2023-10-27T11:10:22Z"),
        ("2023-10-27T11:10:22Z", "2023-10-27T11:10:22Z"),
        ("2023-10-27T10:10:22+02:00", "2023-10-27T08:10:22Z"),
        ("1699625153", "2023-11-10T14:05:53Z"),
        ("1699625153400", "2023-11-10T14:05:53Z"),
        ("2023-11-10T15:05:53Z", "2023-11-10T15:05:53Z"),
        ("2023-11-10T15:05:53.400000Z", "2023-11-10T15:05:53Z"),
        ("2023-10-27", "2023-10-27T00:00:00Z"),
    ],
)
def test_date_to_iso(date, expected):
    assert date_to_iso(parse_date(date)) == expected


def test_extract_hours_and_minutes():
    assert extract_hours_and_minutes("18:31") == (18, 31)
    assert extract_hours_and_minutes("09:31") == (9, 31)
    assert extract_hours_and_minutes("9:31") == (9, 31)


class TestGetBusinessTimeDiff:
    def test_timezone(self):
        start_date = datetime(2022, 11, 9, 11, 20, 0, tzinfo=pytz.FixedOffset(120))
        end_date = datetime(2022, 11, 10, 12, 20, 0, tzinfo=pytz.FixedOffset(120))
        delta = get_business_time_diff(
            start_date, end_date, calendar="FR", business_time_range="09:00-18:00"
        )
        assert delta == 600

    def test_no_timezone(self):
        start_date = datetime(2022, 11, 9, 11, 20, 0, tzinfo=pytz.UTC)
        end_date = datetime(2022, 11, 10, 12, 20, 0, tzinfo=pytz.UTC)
        delta = get_business_time_diff(
            start_date, end_date, calendar="FR", business_time_range="09:00-18:00"
        )
        assert delta == 600

    def test_exclude_local(self):
        start_date = datetime(2022, 11, 10, 12, 00, 0, tzinfo=pytz.UTC)
        end_date = datetime(2022, 11, 14, 12, 00, 0, tzinfo=pytz.UTC)
        delta = get_business_time_diff(
            start_date, end_date, calendar="FR", business_time_range="09:00-18:00"
        )
        assert delta == 9 * 60  # exclude weekends and days off
