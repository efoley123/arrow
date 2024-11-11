import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
import arrow
from datetime import datetime, timedelta
from dateutil import tz
from arrow.factory import ArrowFactory


@pytest.fixture(scope="module")
def arrow_factory():
    return ArrowFactory()


@pytest.fixture
def utcnow():
    return datetime.utcnow()


@pytest.mark.parametrize("input, expected", [
    (None, arrow.Arrow.utcnow().format('YYYY-MM-DD HH:mm:ssZZ')),
    ('2013-05-11T21:23:58.970460+00:00', '2013-05-11T21:23:58.970460+00:00'),
    (1368303838.970460, arrow.Arrow.utcfromtimestamp(1368303838.970460).format('YYYY-MM-DD HH:mm:ssZZ')),
    (1368303838, arrow.Arrow.utcfromtimestamp(1368303838).format('YYYY-MM-DD HH:mm:ssZZ')),
])
def test_get_valid_inputs(arrow_factory, input, expected):
    result = arrow_factory.get(input)
    assert result.format('YYYY-MM-DD HH:mm:ssZZ') == expected


@pytest.mark.parametrize("input", [
    'invalid date string',
    999999999999999999999999,  # timestamp out of range
])
def test_get_invalid_inputs(arrow_factory, input):
    with pytest.raises(ValueError):
        arrow_factory.get(input)


def test_get_with_tzinfo(arrow_factory, utcnow):
    result = arrow_factory.get(utcnow, tzinfo=tz.tzlocal())
    assert result.datetime == utcnow.replace(tzinfo=tz.tzlocal())


def test_get_with_locale(arrow_factory, utcnow):
    result = arrow_factory.get(utcnow, locale='en_us')
    assert result.format('MMMM DD, YYYY') == utcnow.strftime('%B %d, %Y')


def test_get_with_normalization_whitespace(arrow_factory):
    input_date = '2013-05-11     21:23:58.970460+00:00'
    expected = '2013-05-11T21:23:58.970460+00:00'
    result = arrow_factory.get(input_date, normalize_whitespace=True)
    assert result.format('YYYY-MM-DDTHH:mm:ss.SSSSSSZZ') == expected


def test_now_with_tz(arrow_factory):
    result = arrow_factory.now('US/Pacific')
    assert result.datetime.tzinfo == tz.gettz('US/Pacific')


def test_utcnow(arrow_factory):
    result = arrow_factory.utcnow()
    assert result.datetime.tzinfo == tz.tzutc()


class TestArrowFactoryErrors:
    def test_get_none_error(self, arrow_factory):
        with pytest.raises(TypeError):
            arrow_factory.get(None)

    def test_get_unsupported_type_error(self, arrow_factory):
        with pytest.raises(TypeError):
            arrow_factory.get({})

    def test_get_unparsable_string_error(self, arrow_factory):
        with pytest.raises(parser.ParserError):
            arrow_factory.get('unparsable date string')