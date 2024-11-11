import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from arrow import ArrowFactory, Arrow, parser
from arrow.factory import ArrowFactory


# Helper function to mock datetime
def mock_datetime(target, datetime_module):
    class DatetimeSubclassMeta(type):
        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, datetime)

    class BaseMockedDatetime(target):
        @classmethod
        def now(cls, tz=None):
            return datetime_module.now(tz)

        @classmethod
        def utcnow(cls):
            return datetime_module.utcnow()

    MockedDatetime = DatetimeSubclassMeta('datetime', (BaseMockedDatetime,), {})
    return MockedDatetime


@pytest.fixture
def arrow_factory():
    return ArrowFactory()


# Test cases for ArrowFactory.get method

def test_get_without_args(arrow_factory):
    with patch('arrow.factory.Arrow.utcnow') as mock_utcnow:
        mock_datetime_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_utcnow.return_value = mock_datetime_now
        result = arrow_factory.get()
        assert result == mock_datetime_now


def test_get_with_arrow_object(arrow_factory):
    arrow_obj = Arrow(2023, 1, 1)
    result = arrow_factory.get(arrow_obj)
    assert result == arrow_obj


def test_get_with_datetime_object(arrow_factory):
    dt_obj = datetime(2023, 1, 1)
    result = arrow_factory.get(dt_obj)
    assert result.datetime == dt_obj


def test_get_with_timestamp(arrow_factory):
    timestamp = 1672444800  # Corresponds to 2023-01-01 00:00:00 UTC
    with patch('arrow.Arrow.fromtimestamp') as mock_fromtimestamp:
        arrow_factory.get(timestamp)
        mock_fromtimestamp.assert_called_once_with(timestamp, tzinfo=None)


def test_get_with_iso_string(arrow_factory):
    iso_str = '2023-01-01T12:00:00'
    with patch('arrow.parser.DateTimeParser.parse_iso') as mock_parse_iso:
        arrow_factory.get(iso_str)
        mock_parse_iso.assert_called_once_with(iso_str, False)


def test_get_with_unsupported_type_raises_error(arrow_factory):
    with pytest.raises(TypeError):
        arrow_factory.get(object())


def test_get_with_tzinfo(arrow_factory):
    tzinfo = 'US/Pacific'
    with patch('arrow.parser.TzinfoParser.parse') as mock_parse:
        arrow_factory.get(tzinfo=tzinfo)
        mock_parse.assert_called_once_with(tzinfo)


def test_get_with_locale(arrow_factory):
    locale = 'en_us'
    with patch('arrow.Arrow.utcnow') as mock_utcnow:
        mock_datetime_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_utcnow.return_value = mock_datetime_now
        arrow_factory.get(locale=locale)
        mock_utcnow.assert_called_once()


def test_get_with_unsupported_args_raises_error(arrow_factory):
    with pytest.raises(TypeError):
        arrow_factory.get(None)


# Test cases for ArrowFactory.utcnow method

def test_utcnow(arrow_factory):
    with patch('arrow.Arrow.utcnow') as mock_utcnow:
        mock_datetime_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_utcnow.return_value = mock_datetime_now
        result = arrow_factory.utcnow()
        assert result == mock_datetime_now


# Test cases for ArrowFactory.now method

def test_now_with_tzinfo(arrow_factory):
    tzinfo = 'US/Pacific'
    with patch('arrow.Arrow.now') as mock_now:
        mock_datetime_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_now.return_value = mock_datetime_now
        result = arrow_factory.now(tz=tzinfo)
        assert result == mock_datetime_now
        mock_now.assert_called_once_with(parser.TzinfoParser.parse(tzinfo))