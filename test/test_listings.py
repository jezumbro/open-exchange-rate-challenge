from pprint import pprint

import pytest
from listing.model import Listing


@pytest.mark.parametrize(
    "data, msg",
    [
        ({}, "no body in request"),
        (
            {
                "title": "bad market request",
                "base_price": "12",
                "currency": "USD",
                "market": "market",
            },
            "invalid market request",
        ),
        (
            {
                "title": "bad currency request",
                "base_price": "12",
                "currency": "d",
                "market": "san-francisco",
            },
            "invalid currency request",
        ),
        (
            {
                "title": "missing base price",
                "currency": "USD",
                "market": "san-francisco",
            },
            "invalid base price request",
        ),
        (
            {
                "base_price": 1,
                "currency": "USD",
                "market": "san-francisco",
            },
            "missing title request",
        ),
        (
            {
                "title": "bad price format",
                "base_price": "price",
                "currency": "USD",
                "market": "san-francisco",
            },
            "bad price request",
        ),
    ],
)
def test_invalid_listing_requests(client, data, msg):
    resp = client.post("/listings", json=data)
    assert resp.status_code == 422, msg


def test_create_simple_listing(client, simple_listing, tmp_path):
    resp = client.post("/listings", json=simple_listing)
    listing_json = tmp_path / "data" / "listing.json"
    pprint(resp.json)
    assert resp.status_code == 200
    assert listing_json.exists(), "should create json file here"


def test_create_simple_listing_with_host_name(client, simple_listing, tmp_path):
    host_name = "John Smith"
    resp = client.post("/listings", json={**simple_listing, "host_name": host_name})
    listing_json = tmp_path / "data" / "listing.json"
    pprint(resp.json)
    assert resp.status_code == 200
    assert resp.json["host_name"] == host_name
    assert listing_json.exists(), "should create json file here"


def test_get_no_listing_still_returns(client):
    resp = client.get("/listings")
    pprint(resp.json)
    assert resp.status_code == 200
    assert resp.json == list()


@pytest.mark.parametrize(
    "query_param,expected_length,msg",
    [
        ("", 4, "no filter applied all results"),
        ("?market=paris", 2, "paris market only"),
        ("?market=paris,san-francisco", 4, "san-fran and paris"),
    ],
)
def test_filter_listings_based_on_market(
    client, persisted_listings, query_param, expected_length, msg
):
    resp = client.get(f"/listings{query_param}")
    data = resp.json
    pprint(data)
    assert resp.status_code == 200
    assert len({r["id"] for r in data}) == len(data) == expected_length, msg


def test_invalid_data_filters(client, persisted_listings):
    resp = client.get(f"/listings?base_price.e=10")
    data = resp.json
    pprint(data)
    assert resp.status_code == 422, "missing currency parameter"


@pytest.mark.parametrize(
    "query_param,expected_length,msg",
    [
        ("", 4, "no filter applied all results"),
        ("?market=paris", 2, "paris market only"),
        ("?market=paris,san-francisco", 4, "san-fran and paris"),
        ("?base_price.e=10&currency=USD", 1, "only san-fran listing"),
        ("?base_price.lt=10&currency=USD", 0, "lt 10"),
        ("?base_price.gt=10&currency=USD", 3, "gt 10"),
        ("?base_price.gte=11&currency=EUR&market=paris", 1, "paris gte 11"),
        ("?base_price.gte=10&currency=USD&base_price.lt=101", 3, "gte 10 lt 100"),
        ("?base_price.lt=11&currency=EUR", 2, "only the cheep listings"),
        ("?base_price.lt=10&currency=EUR", 1, "only the cheepest US listing"),
        (
            "?base_price.gte=10.25&currency=USD&market=paris",
            2,
            "converting the euro",
        ),
    ],
)
def test_filter_listings_based_on_market(
    client, persisted_listings, query_param, expected_length, msg
):
    _all = client.get("/listings").json
    pprint(_all)
    resp = client.get(f"/listings{query_param}")
    data = resp.json
    pprint(data)
    assert resp.status_code == 200
    assert len({r["id"] for r in data}) == len(data) == expected_length, msg


def test_delete_listing_that_doesnt_exist(client, persisted_listings):
    resp = client.delete("/listings/0")
    print(resp.text)
    assert resp.status_code == 422, "invalid listing"


def test_delete_first_listing(client, default_listings, persisted_listings, tmp_path):
    resp = client.delete(f"/listings/1")
    assert resp.status_code == 200
    assert len(list(Listing.existing(tmp_path))) == len(default_listings) - 1


def test_delete_first_listing_twice(client, persisted_listings):
    resp = client.delete(f"/listings/1")
    assert resp.status_code == 200
    resp = client.delete(f"/listings/1")
    assert resp.status_code == 422, "we already removed the item"


def test_get_item(client, persisted_listings):
    resp = client.get(f"/listings/1")
    assert resp.status_code == 200
    data = resp.json
    assert all((key in data for key in ("id", "market", "currency")))


def test_get_invalid_listing(client, persisted_listings):
    resp = client.get(f"/listings/0")
    assert resp.status_code == 422


def test_update_invalid_listing(client, persisted_listings):
    resp = client.put(f"/listings/0", json={})
    assert resp.status_code == 422


def test_update_listing_to_eur(client, persisted_listings, tmp_path):
    resp = client.put(f"/listings/2", json={"currency": "EUR"})
    assert resp.status_code == 200
    assert resp.json["currency"]["code"] == "EUR"
    assert list(Listing.existing(tmp_path))[1].currency.code == "EUR"


def test_update_to_invalid(client, persisted_listings, tmp_path):
    resp = client.put(f"/listings/2", json={"market": "SAN_FRAN"})
    assert resp.status_code == 422
