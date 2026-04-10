import datetime as dt
import enum

from model.asset import Asset, AssetType
import pandas as pd

from utils.pcalendar import CalendarType

class Index(Asset):
    """Index implementation
    """
    def __init__(self, ticker: str, calendar: CalendarType, m: float = 1, min_lot: int = 1, currency: str = 'BRL',
                 market_data: pd.DataFrame = pd.DataFrame(), **kwargs) -> None:

        super().__init__(ticker=ticker, asset_type=AssetType.index, calendar=calendar, m=m, min_lot=min_lot, days2settle=0,
                         cost_bps=0.0, cost_unit=0.0, currency=currency,
                         market_data=market_data, **kwargs)

    def get_close(self, date: dt.datetime) -> float:
        return self.market_data[self.market_data.index <= date].iat[-1, self.market_data.columns.get_loc('close')].item()
