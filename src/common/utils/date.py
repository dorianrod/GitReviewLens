from datetime import datetime, timedelta, timezone

import holidays
import pytz


def extract_hours_and_minutes(text):
    hours, minutes = map(int, text.split(':'))
    return hours, minutes


def are_dates_equal(date1, date2):
    return (
        date2 and date1 and date1.replace(microsecond=0) == date2.replace(microsecond=0)
    )


def format_to_iso(date):
    return date_to_iso(parse_date(date))


def format_to_utc(date):
    return (
        (parse_date(date).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z') if date else None
    )


def convert_fake_utc_date_to_utc(date, tz):
    date_heure_utc = pytz.timezone(tz).localize(parse_date(date)).astimezone(pytz.utc)

    return date_heure_utc


def round_date_to_day(date):
    return datetime(date.year, date.month, date.day) if date else None


def date_to_iso(date):
    if not date:
        return None

    offset = date.utcoffset()
    date_utc = date + timedelta(seconds=0 if not offset else -offset.total_seconds())
    iso_format_with_z = date_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    return iso_format_with_z


def round_date_to_timestamp(date):
    if not date:
        return None

    return int(date.timestamp())


def get_day_of_week(date):
    if not date:
        return None

    day = date.strftime("%a")
    day_number = date.weekday()
    return f"{day_number} - {day}"


def parse_date(date_str):
    if isinstance(date_str, datetime):
        return set_tz_if_not_set(date_str)

    if not date_str:
        return None

    try:
        return set_tz_if_not_set(datetime.fromisoformat(date_str))
    except Exception:
        pass

    try:
        if len(date_str) > 10:
            # Si la longueur est supérieure à 10, le timestamp est en
            # millisecondes
            timestamp_in_seconds = int(date_str) / 1000
        else:
            # Sinon, le timestamp est en secondes
            timestamp_in_seconds = int(date_str)

        return set_tz_if_not_set(
            datetime.fromtimestamp(timestamp_in_seconds, tz=pytz.utc)
        )
    except Exception:
        pass

    supported_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # Format avec microsecondes et 'Z' pour UTC
        "%Y-%m-%dT%H:%M:%SZ",  # Format sans microsecondes et 'Z' pour UTC
        "%Y-%m-%dT%H:%M:%S.%f",  # Format avec microsecondes (sans 'Z')
        "%Y-%m-%dT%H:%M:%S",  # Format sans microsecondes (sans 'Z')
        "%Y-%m-%d",  # Format sans heure
    ]

    for date_format in supported_formats:
        try:
            return set_tz_if_not_set(datetime.strptime(date_str, date_format))
        except ValueError:
            pass

    if len(date_str) > 19:
        return parse_date(date_str[:19])

    if len(date_str) > 10:
        return parse_date(date_str[:10])

    raise ValueError("Unsupported date format: {}".format(date_str))


def get_business_time_diff(
    start, end, calendar="FR", business_time_range="09:00-18:00"
):
    country_holidays = holidays.country_holidays(calendar)

    total_minutes = 0.0

    start_time_str = business_time_range.split("-")[0]
    end_time_str = business_time_range.split("-")[1]
    # start_time = datetime.strptime(start_time_str, '%H:%M').time()
    # end_time = datetime.strptime(end_time_str, '%H:%M').time()
    start_hours, start_minutes = extract_hours_and_minutes(start_time_str)
    end_hours, end_minutes = extract_hours_and_minutes(end_time_str)

    dates_range = [
        start + timedelta(n)
        for n in range((round_date_to_day(end) - round_date_to_day(start)).days + 1)
    ]
    for date in dates_range:
        if date.weekday() >= 5 or date in country_holidays:
            continue

        # start_timestamp = datetime.combine(date, start_time)
        # end_timestamp = datetime.combine(date, end_time)
        start_timestamp = date.replace(hour=start_hours, minute=start_minutes)
        end_timestamp = date.replace(hour=end_hours, minute=end_minutes)

        if date.date() == start.date():
            start_timestamp = max(start_timestamp, start)

        if date.date() == end.date():
            end_timestamp = min(end_timestamp, end)

        total_minutes += max(
            float(0), (end_timestamp - start_timestamp).total_seconds() // float(60)
        )

    return total_minutes


def is_in_range(date, start_date, end_date):
    if start_date and date < start_date:
        return False

    if end_date and date > end_date:
        return False

    return True


def set_tz_if_not_set(date):
    if date and not date.tzinfo:
        return date.replace(tzinfo=timezone.utc)

    return date
