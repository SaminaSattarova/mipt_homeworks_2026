from dataclasses import dataclass
from datetime import datetime

from polyfactory.factories import DataclassFactory


@dataclass
class Income:
    amount: float
    date: str


class PersonFactory(DataclassFactory[Income]):
    __model__ = Income

    @classmethod
    def date(cls) -> str:
        return datetime.fromordinal()

def income_success():
    pass
