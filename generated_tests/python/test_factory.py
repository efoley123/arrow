import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from arrow import ArrowFactory, Arrow, parser, util
import arrow


class TestArrowFactory:
    def setup_method(self):
        self.factory = ArrowFactory()

    def test_factory_utcnow(self):
        result = self.factory.utcnow()
        assert result is not None
        assert isinstance(result, Arrow)

    def test_factory_now(self):
        with patch('arrow.Arrow.now') as mock_now:
            self.factory.now('US/Pacific')
            mock_now.assert_called_once_with('US/Pacific')

    def test_factory_fromtimestamp(self):
        timestamp = 1627902000
        result = self.factory.fromtimestamp(timestamp)
        assert result.timestamp() == timestamp

    def test_factory_utcfromtimestamp(self):
        timestamp = 1627902000
        result = self.factory.utcfromtimestamp(timestamp)
        assert result.timestamp() == timestamp

    def test_factory_fromdatetime(self):
        dt = datetime(2021, 8, 2)
        result = self.factory.fromdatetime(dt)
        assert result.year == 2021
        assert result.month == 8
        assert result.day == 2

    def test_factory_get(self):
        with patch.object(Arrow, 'now') as mock_now:
            self.factory.get()
            mock_now.assert_called_once_with()

    def test_factory_get_with_tz(self):
        with patch('arrow.Arrow.now') as mock_now:
            self.factory.get(tzinfo='US/Pacific')
            mock_now.assert_called_once_with(tz='US/Pacific')

    def test_factory_get_with_string(self):
        dt_str = '2021-08-02T12:59:45.345123'
        with patch('arrow.parser.DateTimeParser.parse_iso') as mock_parse_iso:
            self.factory.get(dt_str)
            mock_parse_iso.assert_called_once_with(dt_str, False)

    def test_factory_get_with_arg_error(self):
        with pytest.raises(TypeError):
            self.factory.get(None)

    def test_factory_get_with_kwargs_error(self):
        with pytest.raises(ValueError):
            self.factory.get(xyz='abc')

    def test_factory_get_with_struct_time(self):
        struct_time = datetime.now().timetuple()
        result = self.factory.get(struct_time)
        assert isinstance(result, Arrow)

    def test_factory_get_with_iso_tuple(self):
        iso_tuple = (2021, 1, 1)
        result = self.factory.get(iso_tuple)
        assert result.isocalendar()[:3] == iso_tuple

    @pytest.mark.parametrize("input_value,expected_exception", [
        (None, TypeError),
        ('not-a-real-timestamp', ValueError)
    ])
    def test_factory_get_failure_cases(self, input_value, expected_exception):
        with pytest.raises(expected_exception):
            self.factory.get(input_value)


class TestArrowObject:
    def setup_method(self):
        self.arrow_obj = Arrow(2021, 8, 2)

    def test_replace(self):
        result = self.arrow_obj.replace(year=2022)
        assert result.year == 2022
        assert result.month == 8
        assert result.day == 2

    def test_shift(self):
        result = self.arrow_obj.shift(weeks=+1)
        assert result.year == 2021
        assert result.month == 8
        assert result.day == 9

    def test_to_string(self):
        dt_format = 'YYYY-MM-DD HH:mm:ss'
        expected = '2021-08-02 00:00:00'
        assert self.arrow_obj.format(dt_format) == expected

    def test_humanize_locale(self):
        with patch('arrow.locales.EnglishLocale.describe') as mock_describe:
            mock_describe.return_value = 'an hour ago'
            result = self.arrow_obj.humanize(locale='en_us')
            assert result == 'an hour ago'

    def test_dehumanize(self):
        with patch('arrow.Arrow.shift') as mock_shift:
            self.arrow_obj.dehumanize('an hour ago', locale='en_us')
            mock_shift.assert_called()

    def test_is_between(self):
        start = Arrow(2021, 8, 1)
        end = Arrow(2021, 8, 3)
        assert self.arrow_obj.is_between(start, end)

    def test_properties(self):
        assert self.arrow_obj.year == 2021
        assert self.arrow_obj.month == 8
        assert self.arrow_obj.day == 2

    def test_datetime_interactions(self):
        dt = datetime.now()
        arrow_obj = Arrow.fromdatetime(dt)
        assert arrow_obj.datetime == dt

        assert arrow_obj.date() == dt.date()
        assert arrow_obj.time() == dt.time()

    def test_timestamps(self):
        timestamp = 1627902000
        arrow_obj = Arrow.fromtimestamp(timestamp)
        assert arrow_obj.timestamp() == timestamp
        assert isinstance(arrow_obj.int_timestamp, int)
        assert isinstance(arrow_obj.float_timestamp, float)