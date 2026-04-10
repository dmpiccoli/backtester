from abc import ABC
import enum

import pandas as pd
import datetime as dt

from utils.pcalendar import Calendar, CalendarType


class AssetType(enum.Enum):
    future = 0
    provision = 1
    fund = 2
    index = 3
    equity = 4


class Asset(ABC):
    """
    Base class for asset
    
    Should have all the generic information for all assets
    
    Specific data should be implemented in a less generic class
    """
    ticker: str
    asset_type: AssetType
    calendar: Calendar
    m: float
    min_lot: int
    currency: str
    settlement_currency: str
    days2settle: int
    cost_bps: float
    cost_unit: float
    currency: str
    settlement_currency: str
    market_data: pd.DataFrame

    def __init__(self, ticker: str, asset_type: AssetType, calendar: CalendarType = CalendarType.NOCAL, m: float = 1.0, min_lot: int = 1,
                 days2settle: int = 0, cost_bps: float = 0.0, cost_unit: float = 0.0, currency: str = 'BRL', settlement_currency:str = None,
                 market_data: pd.DataFrame = None, **kwargs) -> None:

        self.ticker = ticker
        self.asset_type = asset_type
        self.calendar = Calendar(calendar)
        self.m = m
        self.min_lot = min_lot
        self.days2settle = days2settle
        self.cost_bps = cost_bps
        self.cost_unit = cost_unit
        self.currency = currency
        if settlement_currency is None:
            self.settlement_currency = self.currency
        else:
            self.settlement_currency = settlement_currency
        self.market_data = market_data

        if 'metadata' in kwargs:
            meta_data = kwargs['metadata']

            for k, i in meta_data.items():
                if hasattr(self, k):
                    setattr(self, k, i)

    def get_field(self, date: dt.datetime, field: str):
        return self.market_data[self.market_data.index == date][field].item()
