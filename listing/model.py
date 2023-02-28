from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from itertools import chain
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

from currencies import Currency
from markets import Market


@dataclass
class Listing:
    id: int
    title: str
    base_price: float
    currency: Currency
    market: Market
    host_name: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        market = Market(**data["market"])
        currency = Currency(**data["currency"])
        raw = {**data, "market": market, "currency": currency}
        return Listing(**raw)

    @classmethod
    def existing_lookup(cls, base_dir) -> Dict[int, Listing]:
        return {x.id: x for x in cls.existing(base_dir)}

    @classmethod
    def existing(cls, base_dir: str) -> Iterable[Listing]:
        path = Path(base_dir) / "data" / "listing.json"
        if not path.exists():
            return []
        with open(path, "r") as fp:
            return (Listing.from_dict(x) for x in json.load(fp))

    @classmethod
    def existing_by_id(cls, _id: int, base_dir: str):
        return cls.existing_lookup(base_dir).get(_id)

    @classmethod
    def extend(cls, listings: List[Listing], base_dir: Union[str, Path]):
        data = cls.existing(base_dir)
        cls.write_to_file(chain(data, listings), base_dir)

    @classmethod
    def write_to_file(cls, data: Iterable[Listing], base_dir: str = None):
        path = Path(base_dir) / "data" / "listing.json"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        raw_data = [x.to_dict() for x in data]
        with open(path, "w") as fp:
            json.dump(raw_data, fp)
