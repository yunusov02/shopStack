from datetime import UTC, datetime
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = ZoneInfo("Asia/Tashkent")


def utc_now() -> datetime:
    return datetime.now(UTC)


def to_timezone(value: datetime, tz: ZoneInfo = DEFAULT_TIMEZONE) -> datetime:

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Naive datetime is not allowed")

    return value.astimezone(tz)


print(utc_now())
