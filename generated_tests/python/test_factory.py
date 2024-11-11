import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from arrow import ArrowFactory, Arrow
from arrow.factory import TZ_EXPR
import calendar
from dateutil import tz as dateutil_tz
from decimal import Decimal
from time import struct_time, gmtime
from typing import Union, Tuple, Any


@pytest.fixture(scope="module")
def arrow_factory() -> ArrowFactory:
    return ArrowFactory()


@pytest.fixture
def mock_arrow() -> Mock:
    return Mock(spec=Arrow)


class TestArrowFactory:

    # Test get method with no inputs, should return current time in UTC
    def test_get_no_input(self, arrow_factory: ArrowFactory):
        with patch('arrow.factory.Arrow.utcnow') as mock_utcnow:
            mock_utcnow.return_value = mock_arrow
            result = arrow_factory.get()
            mock_utcnow.assert_called_once()
            assert result == mock_arrow

    # Test get method with single Arrow object
    def test_get_with_arrow_object(self, arrow_factory: ArrowFactory, mock_arrow: Mock):
        result = arrow_factory.get(mock_arrow)
        assert result == mock_arrow

    # Test get method with datetime object
    def test_get_with_datetime(self, arrow_factory: ArrowFactory):
        dt = datetime(2023, 1, 1, tzinfo=dateutil_tz.tzutc())
        with patch.object(Arrow, 'fromdatetime', return_value=mock_arrow) as mock_fromdatetime:
            result = arrow_factory.get(dt)
            mock_fromdatetime.assert_called_once_with(dt, tzinfo=None)
            assert result == mock_arrow

    # Test get method with date object
    def test_get_with_date(self, arrow_factory: ArrowFactory):
        d = datetime(2023, 1, 1).date()
        with patch.object(Arrow, 'fromdate', return_value=mock_arrow) as mock_fromdate:
            result = arrow_factory.get(d)
            mock_fromdate.assert_called_once_with(d, tzinfo=None)
            assert result == mock_arrow

    # Test get with timestamp
    @pytest.mark.parametrize("timestamp", [1609459200, 1609459200.123456])
    def test_get_with_timestamp(self, arrow_factory: ArrowFactory, timestamp: Union[int, float]):
        with patch.object(Arrow, 'fromtimestamp', return_value=mock_arrow) as mock_fromtimestamp:
            result = arrow_factory.get(timestamp)
            mock_fromtimestamp.assert_called_once()
            assert result == mock_arrow

    # Test get with struct_time
    def test_get_with_struct_time(self, arrow_factory: ArrowFactory):
        st_time = gmtime()
        with patch.object(Arrow, 'utcfromtimestamp', return_value=mock_arrow) as mock_utcfromtimestamp:
            result = arrow_factory.get(st_time)
            mock_utcfromtimestamp.assert_called_once_with(calendar.timegm(st_time))
            assert result == mock_arrow

    # Test get with ISO formatted string
    def test_get_with_iso_string(self, arrow_factory: ArrowFactory):
        iso_string = "2023-01-01T12:00:00+00:00"
        with patch('arrow.factory.parser.DateTimeParser', autospec=True) as mock_parser:
            mock_parser.return_value.parse_iso.return_value = datetime(2023, 1, 1, 12)
            with patch.object(Arrow, 'fromdatetime', return_value=mock_arrow):
                result = arrow_factory.get(iso_string)
                assert result == mock_arrow

    # Test get with tuple representing iso calendar
    def test_get_with_iso_calendar_tuple(self, arrow_factory: ArrowFactory):
        iso_calendar_tuple = (2023, 1, 1)  # year, week, day
        with patch('arrow.factory.iso_to_gregorian', return_value=datetime(2023, 1, 3).date()) as mock_iso_to_gregorian:
            with patch.object(Arrow, 'fromdate', return_value=mock_arrow):
                result = arrow_factory.get(iso_calendar_tuple)
                mock_iso_to_gregorian.assert_called_once_with(*iso_calendar_tuple)
                assert result == mock_arrow

    # Test get with unsupported type raises TypeError
    def test_get_with_unsupported_type(self, arrow_factory: ArrowFactory):
        with pytest.raises(TypeError):
            arrow_factory.get([])

    # Test get with None raises TypeError
    def test_get_with_none(self, arrow_factory: ArrowFactory):
        with pytest.raises(TypeError):
            arrow_factory.get(None)

    # Test get with Decimal timestamp
    def test_get_with_decimal(self, arrow_factory: ArrowFactory):
        timestamp = Decimal('1609459200.123456')
        with patch.object(Arrow, 'fromtimestamp', return_value=mock_arrow) as mock_fromtimestamp:
            result = arrow_factory.get(timestamp)
            mock_fromtimestamp.assert_called_once()
            assert result == mock_arrow

    # Test get with datetime and tzinfo
    def test_get_datetime_with_tzinfo(self, arrow_factory: ArrowFactory):
        dt = datetime(2023, 1, 1)
        tzinfo = dateutil_tz.gettz('Europe/London')
        with patch.object(Arrow, 'fromdatetime', return_value=mock_arrow) as mock_fromdatetime:
            result = arrow_factory.get(dt, tzinfo=tzinfo)
            mock_fromdatetime.assert_called_once_with(dt, tzinfo=tzinfo)
            assert result == mock_arrow

    # Test get with string and format list
    def test_get_string_with_format_list(self, arrow_factory: ArrowFactory):
        date_str = '01-01-2023 12:00:00'
        formats = ['DD-MM-YYYY HH:mm:ss', 'YYYY-MM-DD']
        with patch('arrow.factory.parser.DateTimeParser', autospec=True) as mock_parser:
            mock_parser.return_value.parse.return_value = datetime(2023, 1, 1, 12)
            with patch.object(Arrow, 'fromdatetime', return_value=mock_arrow):
                result = arrow_factory.get(date_str, formats)
                assert result == mock_arrow

    # Test now with tzinfo
    @pytest.mark.parametrize("tz_input,tz_expected", [
        (None, dateutil_tz.tzlocal()),
        ('UTC', dateutil_tz.tzutc()),
        ('Europe/London', dateutil_tz.gettz('Europe/London'))
    ])
    def test_now_with_tzinfo(self, arrow_factory: ArrowFactory, tz_input: TZ_EXPR, tz_expected: dt_tzinfo):
        with patch.object(Arrow, 'now', return_value=mock_arrow) as mock_now:
            result = arrow_factory.now(tz_input)
            mock_now.assert_called_once_with(tz_expected)
            assert result == mock_arrow

    # Test utcnow
    def test_utcnow(self, arrow_factory: ArrowFactory):
        with patch.object(Arrow, 'utcnow', return_value=mock_arrow) as mock_utcnow:
            result = arrow_factory.utcnow()
            mock_utcnow.assert_called_once()
            assert result == mock_arrow