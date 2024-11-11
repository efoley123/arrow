import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, tzinfo
from arrow import Arrow, ArrowFactory
from arrow.factory import TZ_EXPR
import pytz
from dateutil import tz as dateutil_tz

# Helper functions
def _mock_now(return_value):
    return patch('arrow.factory.ArrowFactory.utcnow', return_value=return_value)

# Setup and teardown functions if needed
@pytest.fixture
def setup_arrow_factory():
    # Setup if needed, for example, setting a fixed now datetime
    now = Arrow(2023, 1, 1)
    with _mock_now(return_value=now):
        yield now

# Test cases start here
@pytest.mark.usefixtures("setup_arrow_factory")
class TestArrowFactory:
    def test_get_now_without_tz(self):
        """Test getting the current time without specifying timezone."""
        factory = ArrowFactory()
        result = factory.get()
        assert isinstance(result, Arrow)
        assert result == Arrow.utcnow()

    def test_get_now_with_tz(self):
        """Test getting the current time with a specified timezone."""
        factory = ArrowFactory()
        tz = 'US/Pacific'
        result = factory.get(tzinfo=tz)
        assert isinstance(result, Arrow)
        expected = Arrow.utcnow().to(tz)
        assert result.datetime == expected.datetime

    def test_get_with_datetime(self):
        """Test getting Arrow object from datetime."""
        factory = ArrowFactory()
        dt = datetime(2023, 1, 1, tzinfo=dateutil_tz.UTC)
        result = factory.get(dt)
        assert isinstance(result, Arrow)
        assert result.datetime == dt

    def test_get_with_timestamp(self):
        """Test getting Arrow object from timestamp."""
        factory = ArrowFactory()
        timestamp = datetime(2023, 1, 1, tzinfo=dateutil_tz.UTC).timestamp()
        result = factory.get(timestamp)
        assert isinstance(result, Arrow)
        assert result.timestamp() == pytest.approx(timestamp)

    def test_get_with_string(self):
        """Test getting Arrow object from ISO 8601 string."""
        factory = ArrowFactory()
        dt_str = "2023-01-01T00:00:00+00:00"
        result = factory.get(dt_str)
        assert isinstance(result, Arrow)
        assert result.isoformat() == dt_str

    def test_get_with_unsupported_type_raises_error(self):
        """Test that providing an unsupported type raises an error."""
        factory = ArrowFactory()
        with pytest.raises(TypeError):
            factory.get([])  # Passing a list, which is not supported

    def test_get_with_arrow_object(self):
        """Test getting Arrow object from another Arrow object."""
        factory = ArrowFactory()
        original = Arrow(2023, 1, 1)
        result = factory.get(original)
        assert result == original
        assert result is not original  # Ensure a new object is returned

    def test_utcnow(self):
        """Test utcnow method returns correct Arrow object."""
        factory = ArrowFactory()
        with _mock_now(return_value=Arrow(2023, 1, 1)):
            result = factory.utcnow()
            assert isinstance(result, Arrow)
            assert result == Arrow(2023, 1, 1)

    def test_now_with_tz(self):
        """Test now method with specified timezone."""
        factory = ArrowFactory()
        tz = 'US/Pacific'
        result = factory.now(tz)
        assert isinstance(result, Arrow)
        assert result.tzinfo == pytz.timezone(tz)

    def test_get_with_iso_calendar_date(self):
        """Test getting Arrow object from ISO calendar date."""
        factory = ArrowFactory()
        result = factory.get((2023, 1, 1))  # Year 2023, Week 1, Day 1
        assert isinstance(result, Arrow)
        # The first day of the first week of 2023 is 2022-12-26
        assert result.date() == datetime(2022, 12, 26).date()

    def test_get_with_struct_time(self):
        """Test getting Arrow object from struct_time."""
        factory = ArrowFactory()
        struct = datetime(2023, 1, 1, tzinfo=dateutil_tz.UTC).timetuple()
        result = factory.get(struct)
        assert isinstance(result, Arrow)
        assert result.year == 2023 and result.month == 1 and result.day == 1

    def test_get_with_datetime_and_tz_overwrite(self):
        """Test getting Arrow object from datetime and overwriting tzinfo."""
        factory = ArrowFactory()
        dt = datetime(2023, 1, 1)
        tz = 'US/Pacific'
        result = factory.get(dt, tzinfo=tz)
        assert isinstance(result, Arrow)
        assert result.tzinfo == pytz.timezone(tz)
        assert result.year == 2023 and result.month == 1 and result.day == 1