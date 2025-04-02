import pytest
from datetime import datetime, timezone, timedelta
from nicHelper.datetime import datestamp, stringToTimestamp


def test_datestamp_default():
    """Test datestamp with default arguments (UTC)."""
    now = datetime.now(timezone.utc)
    expected_ts = datetime(
        now.year, now.month, now.day, tzinfo=timezone.utc
    ).timestamp()
    assert datestamp() == int(expected_ts)


def test_datestamp_specific_datetime_utc():
    """Test datestamp with a specific datetime in UTC."""
    dt = datetime(2023, 10, 26, 14, 30, 0, tzinfo=timezone.utc)
    expected_ts = datetime(2023, 10, 26, tzinfo=timezone.utc).timestamp()
    assert datestamp(dt=dt) == int(expected_ts)


def test_datestamp_specific_datetime_other_tz():
    """Test datestamp with a specific datetime and timezone."""
    tz_pdt = timezone(timedelta(hours=-7))
    dt = datetime(2023, 10, 26, 10, 0, 0, tzinfo=tz_pdt)  # 10 AM PDT

    # Expected datestamp should be based on the date in PDT
    expected_ts = datetime(2023, 10, 26, tzinfo=tz_pdt).timestamp()
    assert datestamp(dt=dt, tz=tz_pdt) == int(expected_ts)

    # Test converting to UTC datestamp
    expected_utc_ts = datetime(2023, 10, 26, tzinfo=timezone.utc).timestamp()
    assert datestamp(dt=dt, tz=timezone.utc) == int(expected_utc_ts)


def test_string_to_timestamp_utc():
    """Test stringToTimestamp with default UTC timezone."""
    time_str = "2023-10-26 15:45:00"
    fmt = "%Y-%m-%d %H:%M:%S"
    expected_dt = datetime(2023, 10, 26, 15, 45, 0, tzinfo=timezone.utc)
    expected_ts = expected_dt.timestamp()
    assert stringToTimestamp(time_str, fmt) == expected_ts


def test_string_to_timestamp_specific_tz():
    """Test stringToTimestamp with a specific timezone."""
    time_str = "2023/10/26 10:30:00 AM"
    fmt = "%Y/%m/%d %I:%M:%S %p"
    tz_est = timezone(timedelta(hours=-5))  # EST

    expected_dt = datetime(2023, 10, 26, 10, 30, 0, tzinfo=tz_est)
    expected_ts = expected_dt.timestamp()

    assert stringToTimestamp(time_str, fmt, timeZone=tz_est) == expected_ts


def test_string_to_timestamp_invalid_format():
    """Test stringToTimestamp with a format mismatch."""
    time_str = "26-10-2023"
    fmt = "%Y-%m-%d"  # Format doesn't match the string

    with pytest.raises(ValueError):
        stringToTimestamp(time_str, fmt)
