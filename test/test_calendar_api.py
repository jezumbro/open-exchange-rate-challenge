from datetime import date

import pytest
from calendar_api import (
    build_calendar,
    calendar_lookup,
    default_calendar,
    paris_calendar,
    san_fran_calendar,
)
from markets import Markets


def test_build_calendar(listing):
    q = list(build_calendar(listing, 1, listing.currency))
    assert len(q) == 365


def test_lookup_has_all_markets():
    assert not (
        calendar_lookup.keys() - Markets.__PER_CODE__.keys()
    ), "custom calendar per market"


@pytest.mark.parametrize("dt,expected", (("2022-01-01", 1), ("2022-01-05", 0.7)))
def test_san_fran_calendar(dt, expected):
    assert san_fran_calendar(date.fromisoformat(dt)) == expected


@pytest.mark.parametrize("dt,expected", (("2022-01-01", 1.5), ("2022-01-03", 1)))
def test_paris_calendar(dt, expected):
    assert paris_calendar(date.fromisoformat(dt)) == expected


@pytest.mark.parametrize("dt,expected", (("2022-01-01", 1), ("2022-01-07", 1.25)))
def test_default_calendar(dt, expected):
    assert default_calendar(date.fromisoformat(dt)) == expected
