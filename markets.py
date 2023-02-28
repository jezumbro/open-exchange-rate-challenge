from dataclasses import asdict, dataclass

from currencies import CurrencyEnum


@dataclass
class Market:
    code: str
    name: str
    currency: str

    def to_dict(self):
        return asdict(self)


class InvalidMarket(Exception):
    pass


class Markets:
    # Codes
    SAN_FRANCISCO = "san-francisco"
    LISBON = "lisbon"
    PARIS = "paris"
    TOKYO = "tokyo"
    JERUSALEM = "jerusalem"
    BRISBANE = "brisbane"

    __ALL__ = [
        Market(SAN_FRANCISCO, "San Francisco", CurrencyEnum.USD),
        Market(LISBON, "Lisbon", CurrencyEnum.EUR),
        Market(PARIS, "Paris", CurrencyEnum.EUR),
        Market(TOKYO, "Tokyo", CurrencyEnum.JPY),
        Market(JERUSALEM, "Jerusalem", CurrencyEnum.ILS),
        Market(BRISBANE, "Brisbane", CurrencyEnum.AUD),
    ]

    __PER_CODE__ = {market.code: market for market in __ALL__}

    @classmethod
    def get_all(cls):
        return cls.__ALL__

    @classmethod
    def get_by_code(cls, code):
        if market := cls.__PER_CODE__.get(code):
            return market
        raise InvalidMarket(f"Market with code={code} does not exist")
