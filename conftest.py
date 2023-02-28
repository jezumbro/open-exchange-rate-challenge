import pytest
from flask.testing import FlaskClient

from app import app
from currencies import Currencies, Currency
from listing.api import convert_request_to_new_listing
from listing.model import Listing
from markets import Markets
from open_exchange import get_rate_converter


@pytest.fixture()
def client(tmp_path) -> FlaskClient:
    app.config["BASE_DIR"] = tmp_path
    app.config["TESTING"] = True
    app.rate_converter = get_rate_converter(True)
    with app.test_client() as client:
        yield client


@pytest.fixture
def default_listings():
    existing_listings = []
    for data in [
        {
            "title": "san fran 100",
            "base_price": 100,
            "currency": "USD",
            "market": "san-francisco",
        },
        {
            "title": "san fran 10",
            "base_price": 10,
            "currency": "USD",
            "market": "san-francisco",
        },
        {
            "title": "paris 10",
            "base_price": 10,
            "currency": "EUR",
            "market": "paris",
        },
        {
            "title": "paris 100",
            "base_price": 100,
            "currency": "EUR",
            "market": "paris",
        },
    ]:
        new_listing = convert_request_to_new_listing(data, existing_listings)
        existing_listings.append(new_listing)
    return existing_listings


@pytest.fixture
def persisted_listings(tmp_path, default_listings):
    Listing.extend(default_listings, tmp_path)
    return


@pytest.fixture
def simple_listing():
    return {
        "title": "simple listing",
        "base_price": 1,
        "currency": "USD",
        "market": "san-francisco",
    }


@pytest.fixture
def listing():
    return Listing(
        id=0,
        title="some title",
        base_price=100,
        currency=Currencies.get_by_code("USD"),
        market=Markets.get_by_code("san-francisco"),
    )
