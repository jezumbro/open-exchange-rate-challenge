from itertools import chain
from typing import Dict, Iterable, List

from currencies import Currencies, Currency, InvalidCurrency
from flask import Request, jsonify
from invalid import InvalidRequest
from markets import InvalidMarket, Markets
from open_exchange import RateConverter, convert_rate

from listing.model import Listing


def validate_market(data: dict):
    try:
        return Markets.get_by_code(data.get("market", ""))
    except InvalidMarket as e:
        raise InvalidRequest(e.args[0])


def validate_currency(data: dict):
    try:
        return Currencies.get_by_code(data.get("currency", ""))
    except InvalidCurrency as e:
        raise InvalidRequest(e.args[0])


def validate_price(data: dict):
    try:
        return float(data.get("base_price"))
    except ValueError as e:
        raise InvalidRequest(e.args[0])


def validate_title(data: dict):
    if title := data.get("title"):
        return title
    raise InvalidRequest("must include a title")


required_keys = {
    "market": validate_market,
    "currency": validate_currency,
    "title": validate_title,
    "base_price": validate_price,
}

optional_keys = {**required_keys, "host_name": None}


def new_listing_id(existing_listings: List[Listing]):
    return max((listing.id for listing in existing_listings), default=0) + 1


def convert_request_to_new_listing(data: dict, existing_listings=None) -> Listing:
    if not data:
        raise InvalidRequest("must include listing data")
    ret = {}
    for key, func in required_keys.items():
        if key not in data:
            raise InvalidRequest(f"missing data key={key}")
        if func:
            ret[key] = func(data)
    new_listing_data = {**data, **ret}
    return Listing(**new_listing_data, id=new_listing_id(existing_listings or list()))


def create_new_listing(base_dir: str, data):
    existing = list(Listing.existing(base_dir))
    listing = convert_request_to_new_listing(data, existing_listings=existing)
    Listing.write_to_file(chain(existing, [listing]), base_dir)
    return jsonify(listing.to_dict())


def base_prices_in_request(params: dict):
    return {k: v for k, v in params.items() if k.startswith("base_price")}


base_price_filter_lkp = {
    "e": lambda listing, price: listing.base_price == price,
    "lt": lambda listing, price: listing.base_price < price,
    "lte": lambda listing, price: listing.base_price <= price,
    "gt": lambda listing, price: listing.base_price > price,
    "gte": lambda listing, price: listing.base_price >= price,
}


def rate_listing_filter(
    listings: Iterable[Listing],
    rates: dict,
    base_code: str,
    price_func: callable,
    price: float,
):
    for listing in listings:
        rate = convert_rate(rates, base_code)
        converted_price = price * rate.get(listing.currency.code, 1)
        if price_func(listing, converted_price):
            yield listing


def filter_listings(
    listings: Iterable[Listing], params: dict, rate_converter: RateConverter
) -> Iterable[Listing]:
    if markets := params.get("market"):
        market_set = set(markets.split(","))
        listings = (
            listing for listing in listings if listing.market.code in market_set
        )
    if base_prices := base_prices_in_request(params):
        currency: Currency = validate_currency(params)
        if not currency:
            raise InvalidRequest("must include currency when querying using base price")
        rates = rate_converter.latest_rates(currency.code)
        for base_price_key, base_price in base_prices.items():
            price = parse_float(base_price, base_price_key)
            lkp_key = base_price_key.split(".")[-1]
            if price_func := base_price_filter_lkp.get(lkp_key):
                listings = rate_listing_filter(
                    listings, rates, currency.code, price_func, price
                )
    return listings


def parse_float(base_price, base_price_key):
    try:
        return float(base_price)
    except ValueError:
        raise InvalidRequest(f"Unable to parse {base_price_key}={base_price}")


def listing_get_request(request: Request, base_dir: str, rate_converter: RateConverter):
    existing = Listing.existing(base_dir)
    filtered_listings = filter_listings(existing, request.args, rate_converter)
    return jsonify([x.to_dict() for x in filtered_listings])


def delete_listing_by_id(existing_lkp, listing_id: int, base_dir: str):
    if listing_id in existing_lkp:
        existing_lkp.pop(listing_id)
        Listing.write_to_file(existing_lkp.values(), base_dir)
        return "success"
    raise InvalidRequest("unable to find listing")


def listing_by_id(existing_lkp: Dict[int, Listing], listing_id: int, **kwargs):
    if listing := existing_lkp.get(listing_id):
        return jsonify(listing)
    raise InvalidRequest("unable to find listing")


def update_existing_listing(
    existing_lkp: Dict[int, Listing], listing_id: int, base_dir: str, new_data: dict
):
    if listing_id not in existing_lkp:
        raise InvalidRequest("unable to find listing")
    listing = existing_lkp[listing_id]
    for key, value in new_data.items():
        if key not in optional_keys:
            continue
        if key in required_keys:
            setattr(listing, key, required_keys[key](new_data))
            continue
        setattr(listing, key, value)
    Listing.write_to_file(existing_lkp.values(), base_dir)
    return jsonify(listing)
