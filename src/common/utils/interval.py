from datetime import timedelta


def timedelta_to_minutes(td):
    return td.days * 24 * 60 + td.seconds // 60


def get_interval_to_minutes(interval_str):
    if not interval_str:
        return None

    if interval_str.endswith("h"):
        hours = int(interval_str[:-1])
        return timedelta_to_minutes(timedelta(hours=hours))
    elif interval_str.endswith("d"):
        days = int(interval_str[:-1])
        return timedelta_to_minutes(timedelta(days=days))
    else:
        raise ValueError("Not implemented interval type")
