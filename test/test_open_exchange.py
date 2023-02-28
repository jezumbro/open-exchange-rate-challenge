import pytest
from open_exchange import convert_rate


@pytest.fixture
def rate_fixture():
    return {"AUD": 1.358192, "EUR": 0.847971, "ILS": 3.264521, "JPY": 110.286, "USD": 1}


def test_convert_rate(rate_fixture):
    out = convert_rate(rate_fixture, "USD")
    assert out == rate_fixture


def test_convert_to_EUR(rate_fixture):
    out = convert_rate(rate_fixture, "EUR")
    assert out["EUR"] == 1
    assert out["USD"] > 1
