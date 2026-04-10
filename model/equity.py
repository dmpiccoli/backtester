import datetime as dt
import enum

from model.asset import Asset, AssetType
import pandas as pd

from utils.pcalendar import CalendarType

class Equity(Asset):
    """Equity implementation
    """
    def __init__(self, ticker: str, calendar: CalendarType, m: float = 1, min_lot: int = 1, days2settle: int = 0,
                 cost_bps: float = 1 / 10000, cost_unit: float = 0.0, currency: str = 'BRL', settlement_currency: str = None,
                 market_data: pd.DataFrame = pd.DataFrame(), **kwargs) -> None:

        super().__init__(ticker=ticker, asset_type=AssetType.equity, calendar=calendar, m=m, min_lot=min_lot, days2settle=days2settle,
                         cost_bps=cost_bps, cost_unit=cost_unit, currency=currency, settlement_currency=settlement_currency,
                         market_data=market_data, **kwargs)

    def get_close(self, date: dt.datetime) -> float:
        return self.market_data[self.market_data.index <= date].iat[-1, self.market_data.columns.get_loc('close')].item()
