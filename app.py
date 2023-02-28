from flask import Flask, jsonify, request

from calendar_api import build_calendar
from currencies import Currency
from invalid import InvalidRequest
from listing.api import (
    create_new_listing,
    delete_listing_by_id,
    listing_by_id,
    listing_get_request,
    update_existing_listing,
    validate_currency,
)
from listing.model import Listing
from markets import Markets
from open_exchange import RateConverter, get_rate_converter, latest_rates

app = Flask(__name__)
app.rate_converter = get_rate_converter(app.testing)


@app.errorhandler(InvalidRequest)
def handle_invalid_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/markets")
def markets():
    return jsonify([market.to_dict() for market in Markets.get_all()])


@app.get("/listings")
def get_listings():
    base_dir = app.config.get("BASE_DIR", ".")
    return listing_get_request(request, base_dir, app.rate_converter)


@app.post("/listings")
def post_listings():
    base_dir = app.config.get("BASE_DIR", ".")
    return create_new_listing(base_dir, request.json)


@app.get("/listings/<int:listing_id>")
def get_listing(listing_id: int):
    base_dir = app.config.get("BASE_DIR", ".")
    existing_lkp = Listing.existing_lookup(base_dir)
    return listing_by_id(existing_lkp, listing_id)


@app.put("/listings/<int:listing_id>")
def put_listing(listing_id: int):
    base_dir = app.config.get("BASE_DIR", ".")
    existing_lkp = Listing.existing_lookup(base_dir)
    return update_existing_listing(existing_lkp, listing_id, base_dir, request.json)


@app.delete("/listings/<int:listing_id>")
def delete_listing(listing_id: int):
    base_dir = app.config.get("BASE_DIR", ".")
    return delete_listing_by_id(Listing.existing_lookup(base_dir), listing_id, base_dir)


@app.route("/listings/<int:listing_id>/calendar", methods=["GET"])
def listing_calendar(listing_id: int):
    local_listing = Listing.existing_by_id(listing_id, app.config.get("BASE_DIR", "."))
    if not local_listing:
        raise InvalidRequest("unable to find listing")
    rates = {}
    currency = local_listing.currency
    if "currency" in request.args:
        currency: Currency = validate_currency(request.args)
        rates = app.rate_converter.latest_rates(currency.code)
    return jsonify(
        list(
            build_calendar(
                local_listing, rates.get(local_listing.currency.code, 1), currency.code
            )
        )
    )
