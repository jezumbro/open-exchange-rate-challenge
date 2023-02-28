import os

import requests
from cachetools import TTLCache, cached
from dotenv import load_dotenv

from currencies import Currencies, CurrencyEnum

base_url = "https://openexchangerates.org/api"

load_dotenv()


@cached(cache=TTLCache(maxsize=2, ttl=10))
def latest_rates(base_code: str = CurrencyEnum.USD) -> dict:
    api_key = os.getenv("OPEN_EXCHANGE_API")
    if not api_key:
        raise Exception("Are you sure you set the OPEN_EXCHANGE_API env key")
    codes = Currencies.codes()
    resp = requests.post(
        f"{base_url}/latest.json",
        params={"app_id": api_key, "symbols": ",".join(codes)},
    )
    if resp.ok:
        data = resp.json().get("rates", {})
        return convert_rate(data, base_code)
    print("UNABLE to get exchange rates", resp.status_code, resp.text)
    return {}


def convert_rate(data: dict, base_code: str):
    if base_code != CurrencyEnum.USD:
        rate = data.get(base_code, 1)
        return {k: v / rate for k, v in data.items()}
    return data


class RateConverter:
    def __init__(self, testing: bool):
        self.testing = testing

    def latest_rates(self, base_code: str):
        if self.testing:
            return {CurrencyEnum.USD: 1, CurrencyEnum.EUR: 0.94}
        return latest_rates(base_code)


def get_rate_converter(testing):
    return RateConverter(testing)
