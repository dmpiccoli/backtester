import datetime as dt
import math

import numpy as np

from data.data_manager import DataManager
from utils.pcalendar import CalendarType
from model.portfolio.portfolio import Portfolio
from model.portfolio_manager.portfolio_manager import PortfolioManager


class Rsi(PortfolioManager):
    def __init__(self, name: str, w: int = 21, vol_target: float = 0.08, first_trade: dt.datetime = dt.datetime(2000, 1, 1), trade_calendar: CalendarType = CalendarType.B3,
                 portfolio_calendar: CalendarType = CalendarType.BR, portfolio: Portfolio | None = None) -> None:

        super().__init__(name, first_trade, trade_calendar, portfolio_calendar, portfolio)

        self.w = w
        self.vol_target = vol_target

        pass

    def load_data(self, ticker:str, update=False):
        self.data = DataManager().load(ticker)[ticker].market_data
        pass

    def once(self):
        self.data = self.data.loc[~self.data['close'].isna()]
        self.data = self.data.loc[~self.data['volume'].isna()]
        self.data['r'] = self.data['close'].diff()
        self.data['gain'] = self.data['r'].clip(lower=0)
        self.data['loss'] = self.data['r'].clip(upper=0).abs()

        self.data['gain'] = self.data['gain'].ewm(alpha=1/self.w, adjust=False, min_periods=self.w).mean()
        self.data['loss'] = self.data['loss'].ewm(alpha=1/self.w, adjust=False, min_periods=self.w).mean()

        self.data['rsi'] = self.data['gain'] / self.data['loss']
        self.data['rsi'] = 100 - (100 / (1 + self.data['rsi']))
        self.data['rsi'] = self.data['rsi']

        self.data['vol'] = np.log(self.data['close']).diff().ewm(alpha=0.04).std() * math.sqrt(252)
        self.data['size'] = self.vol_target / self.data['vol']
        self.data['high_1'] = self.data['high'].shift(1)
        self.data = self.data.drop(['gain', 'loss', 'r'], axis=1, errors='ignore')

    def next(self, date: dt.datetime):
        if date in self.data.index:
            ticker = self.data.loc[self.data.index == date]['ticker'].values[0]
            q = DataManager().load(ticker)[ticker]
            signal = self.data.loc[self.data.index == date]['rsi'].values[0]
            pct_size = self.data.loc[self.data.index == date]['size'].values[0]
            price = self.data.loc[self.data.index == date]['close'].values[0]
            last_high = self.data.loc[self.data.index == date]['high_1'].values[0]

            current_port = self.portfolio.get_data_by_date(date)
            nav = current_port.iat[0, current_port.columns.get_loc('NAV')]
            current_pos = self.portfolio.get_positions_d1(date)

            if current_pos.empty and signal <= 20:
                self.portfolio.add_order_equity(date=date, ticker=ticker, qty=pct_size * nav / price / q.m)
            elif not current_pos.empty and price > last_high:
                qty = current_pos.loc[current_pos.ticker == ticker]['qty'][0]
                self.portfolio.add_order_equity(date=date, ticker=ticker, qty=-qty)
        pass
