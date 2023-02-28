from datetime import datetime, timedelta

import pytest


@pytest.mark.parametrize(
    "url,msg",
    [
        ("/0/calendar", "invalid listing"),
        ("/1/calendar?currency=usd", "invalid currency"),
    ],
)
def test_invalid_listing_for_calendar(client, persisted_listings, url, msg):
    resp = client.get(f"/listings{url}")
    assert resp.status_code == 422, msg


def test_calendar_date_range(client, persisted_listings):
    resp = client.get(f"/listings/1/calendar")
    data = resp.json
    dates = [datetime.strptime(row["date"], "%Y-%m-%d").date() for row in data]
    now = datetime.now().date()
    assert min(dates).isoformat() == now.isoformat()
    assert len(data) == 365, "365 days in dataset"
