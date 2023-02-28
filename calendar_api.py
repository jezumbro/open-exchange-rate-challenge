from datetime import date, datetime, timedelta

from listing.model import Listing
from markets import Markets


def default_calendar(dt: date) -> float:
    if dt.weekday() == 4:
        return 1.25
    return 1


def san_fran_calendar(dt: date) -> float:
    if dt.weekday() == 2:
        return 0.7
    return 1


def paris_calendar(dt: date) -> float:
    if dt.weekday() >= 5:
        return 1.5
    return 1


CALENDARS = {
    Markets.PARIS: paris_calendar,
    Markets.LISBON: paris_calendar,
    Markets.SAN_FRANCISCO: san_fran_calendar,
}


def build_calendar(listing: Listing, currency_factor: float, code: str):
    calendar_multiplier = CALENDARS.get(listing.market.code, default_calendar)
    start = datetime.now().date()
    for day in range(365):
        dt = start + timedelta(days=day)
        yield {
            "date": dt.isoformat(),
            "price": (listing.base_price * calendar_multiplier(dt)) / currency_factor,
            "currency": code,
        }
