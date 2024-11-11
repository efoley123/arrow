import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from arrow import ArrowFactory, Arrow
from arrow.factory import TZ_EXPR
import pytz


# Setup and teardown functions can be defined if needed, for example:
@pytest.fixture
def arrow_factory():
    return ArrowFactory()


# Example of a normal case test
def test_get_now(arrow_factory):
    result = arrow_factory.get()
    assert result is not None
    assert isinstance(result, Arrow)


# Example of an edge case test
def test_get_specific_time(arrow_factory):
    specific_time = datetime(2023, 1, 1, 12, 34, 56)
    with patch("arrow.factory.Arrow.utcnow") as mock_utcnow:
        mock_utcnow.return_value = specific_time
        result = arrow_factory.get()
        assert result == specific_time


# Example of an error case test
@pytest.mark.parametrize("input_value", [None, "invalid-string", 999999999999999999999999999])
def test_get_with_invalid_input_raises_error(arrow_factory, input_value):
    with pytest.raises(TypeError):
        arrow_factory.get(input_value)


# Test datetime input
def test_get_with_datetime(arrow_factory):
    dt = datetime(2020, 5, 17, 15, 30, tzinfo=pytz.utc)
    result = arrow_factory.get(dt)
    assert result.datetime == dt


# Test string input
def test_get_with_string(arrow_factory):
    dt_string = "2020-05-17T15:30:00+00:00"
    result = arrow_factory.get(dt_string)
    assert result.format("YYYY-MM-DDTHH:mm:ssZZ") == dt_string


# Test timestamp input
def test_get_with_timestamp(arrow_factory):
    timestamp = 1589725800  # corresponds to 2020-05-17T15:30:00+00:00
    result = arrow_factory.get(timestamp)
    assert result.timestamp() == timestamp


# Test tzinfo conversion
@pytest.mark.parametrize("tz_input, expected_tz", [
    (pytz.timezone("US/Pacific"), "US/Pacific"),
    ("US/Pacific", "US/Pacific"),
    (pytz.utc, "UTC"),
])
def test_get_with_tzinfo(arrow_factory, tz_input: TZ_EXPR, expected_tz: str):
    result = arrow_factory.get(tzinfo=tz_input)
    assert result.datetime.tzinfo.zone == expected_tz


# Test normalization whitespace
def test_get_with_normalization(arrow_factory):
    dt_string = "2020-05-17    T15:30:00+00:00"  # Intentionally added extra spaces
    result = arrow_factory.get(dt_string, normalize_whitespace=True)
    expected_string = "2020-05-17T15:30:00+00:00"
    assert result.format("YYYY-MM-DDTHH:mm:ssZZ") == expected_string


# Test Arrow object input (copying an Arrow object)
def test_get_with_arrow_object(arrow_factory):
    original = Arrow(2020, 5, 17, 15, 30)
    result = arrow_factory.get(original)
    assert result == original
    assert result is not original  # Ensures a new object is returned


# Test struct_time input
def test_get_with_struct_time(arrow_factory):
    struct_time = datetime(2020, 5, 17, 15, 30).timetuple()
    result = arrow_factory.get(struct_time)
    assert result.format("YYYY-MM-DD HH:mm:ss") == "2020-05-17 15:30:00"


# Test ISO calendar input
def test_get_with_iso_calendar(arrow_factory):
    iso_calendar = (2020, 20, 7)  # 2020-W20-7
    result = arrow_factory.get(iso_calendar)
    assert result.format("YYYY-MM-DD") == "2020-05-17"  # The date of 2020-W20-7


# Test list of formats input
def test_get_with_list_of_formats(arrow_factory):
    dt_string = "17-05-2020 15:30"
    result = arrow_factory.get(dt_string, ["DD-MM-YYYY HH:mm", "YYYY-MM-DD HH:mm"])
    assert result.format("YYYY-MM-DD HH:mm") == "2020-05-17 15:30"


# Test for now functionality with tzinfo
def test_factory_now_with_tzinfo(arrow_factory):
    result = arrow_factory.now('US/Pacific')
    assert result is not None
    assert result.datetime.tzinfo.zone == 'US/Pacific'


# Test utcnow functionality
def test_factory_utcnow(arrow_factory):
    result = arrow_factory.utcnow()
    assert result is not None
    assert result.datetime.tzinfo.zone == 'UTC'