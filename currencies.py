from dataclasses import asdict, dataclass
from enum import Enum


@dataclass
class Currency:
    code: str
    name: str
    symbol: str

    def to_dict(self):
        return asdict(self)


class InvalidCurrency(Exception):
    pass


class CurrencyEnum(str, Enum):
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    ILS = "ILS"
    AUD = "AUD"


class Currencies:

    # Define all currencies
    __ALL__ = [
        Currency(CurrencyEnum.USD, "United States Dollar", "$"),
        Currency(CurrencyEnum.EUR, "Euro", "€"),
        Currency(CurrencyEnum.JPY, "Japanese Yen", "¥"),
        Currency(CurrencyEnum.ILS, "Israeli shekel", "₪"),
        Currency(CurrencyEnum.AUD, "Australian Dollar", "A$"),
    ]
    # Organize per code for convenience
    __PER_CODE__ = {currency.code: currency for currency in __ALL__}

    @classmethod
    def codes(cls):
        return [currency.code for currency in cls.__ALL__]

    @classmethod
    def get_all(cls):
        return cls.__ALL__

    @classmethod
    def get_by_code(cls, code):
        if currency := cls.__PER_CODE__.get(code):
            return currency
        raise InvalidCurrency(f"Currency with code={code} does not exist")
