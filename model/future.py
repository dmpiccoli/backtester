import datetime as dt
import enum

from model.asset import Asset, AssetType
import pandas as pd

from utils.pcalendar import CalendarType

class FutureCode(enum.Enum):
    F = 1
    G = 2
    H = 3
    J = 4
    K = 5
    M = 6
    N = 7
    Q = 8
    U = 9
    V = 10
    X = 11
    Z = 12


class Future(Asset):
    """Future implementation
    """
    maturity: dt.datetime
    first_notice: dt.datetime

    def __init__(self, ticker: str, calendar: CalendarType, maturity: dt.datetime, first_notice: dt.datetime = None, m: float = 1, min_lot: int = 1, days2settle: int = 0,
                 cost_bps: float = 1 / 10000, cost_unit: float = 0.0, currency: str = 'BRL', settlement_currency: str = None,
                 market_data: pd.DataFrame = pd.DataFrame(), **kwargs) -> None:

        super().__init__(ticker=ticker, asset_type=AssetType.future, calendar=calendar, m=m, min_lot=min_lot, days2settle=days2settle,
                         cost_bps=cost_bps, cost_unit=cost_unit, currency=currency, settlement_currency=settlement_currency,
                         market_data=market_data, **kwargs)
        self.maturity = maturity

        if first_notice is None:
            self.first_notice = self.maturity
        else:
            self.first_notice = first_notice

    def get_close(self, date: dt.datetime) -> float:
        if date > self.maturity:
            return 0.0
        else:
            return self.market_data[self.market_data.index <= date].iat[-1, self.market_data.columns.get_loc('close')].item()
