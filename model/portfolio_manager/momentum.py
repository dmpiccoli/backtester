import datetime as dt
import math

import numpy as np

from data.data_manager import DataManager
from utils.pcalendar import CalendarType
from model.portfolio.portfolio import Portfolio
from model.portfolio_manager.portfolio_manager import PortfolioManager



class Momentum(PortfolioManager):
    def __init__(self, name: str, w: int = 21, vol_target: float = 0.08, first_trade: dt.datetime = dt.datetime(2000, 1, 1), trade_calendar: CalendarType = CalendarType.B3,
                 portfolio_calendar: CalendarType = CalendarType.BR, portfolio: Portfolio = None) -> None:

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
        self.data['r'] = np.log(self.data['close'] / self.data['close'].shift())
        self.data['vol'] = self.data['r'].ewm(alpha=0.04).std() * math.sqrt(252)
        self.data['size'] = self.vol_target / self.data['vol']
        self.data['momentum'] = self.data['r'].rolling(self.w).sum()
        # self.data['r'] = self.data['r'] - 1
        self.data['signal'] = 0
        self.data.loc[self.data['momentum'] > 0, 'signal'] = 1
        self.data.loc[self.data['momentum'] < 0, 'signal'] = -1

    def next(self, date: dt.datetime):
        if date in self.data.index:
            ticker = self.data.loc[self.data.index == date]['ticker'].values[0]
            q = DataManager().load(ticker)[ticker]
            signal = self.data.loc[self.data.index == date]['signal'].values[0]
            pct_size = self.data.loc[self.data.index == date]['size'].values[0]
            price = self.data.loc[self.data.index == date]['close'].values[0]

            current_port = self.portfolio.get_data(date)
            nav = current_port.iat[0, current_port.columns.get_loc('NAV')]
            current_pos = self.portfolio.get_positions_d1(date)

            #First date
            if current_pos.empty:
                self.portfolio.add_order_equity(date=date, ticker=ticker, qty=pct_size * nav / price / q.m)
            else:
                qty = current_pos.loc[current_pos.ticker == ticker]['qty'][0]
                self.portfolio.add_order_equity(date=date, ticker=ticker, qty=pct_size * nav / price / q.m - qty)
        pass
