import datetime as dt

import pandas as pd

from data.data_manager import DataManager
from model.future import FutureCode
from utils.pcalendar import CalendarType
from model.portfolio.portfolio import Portfolio
from model.portfolio_manager.portfolio_manager import PortfolioManager


class RiskParity(PortfolioManager):
    def __init__(self, name: str, first_trade: dt.datetime = dt.datetime(2000, 1, 1), trade_calendar: CalendarType = CalendarType.B3,
                 portfolio_calendar: CalendarType = CalendarType.BR, portfolio: Portfolio = None) -> None:

        super().__init__(name, first_trade, trade_calendar, portfolio_calendar, portfolio)
        pass

    def load_data(self, tickers:list, update=False):
        d = DataManager().load(ticker=tickers)

    def once(self):
        pass

    def next(self, date: dt.datetime):
        current_port = self.portfolio.get_data(date)
        nav = current_port.iat[0, current_port.columns.get_loc('NAV')]
        current_pos = self.portfolio.get_positions_d1(date)

        ticker_buy = None
        ticker_sell = None

        if date in self.data.index:
            i = self.data.index.get_loc(date)
            if self.data.index[i + 2].month != date.month == 12:
                # sell current position
                ticker_sell = current_pos.iloc[0]['ticker']
                # buy next contract
                ticker_buy = 'UC' + FutureCode((date.month+1) % 12 + 1).name + str(date.year - 2000 + 1).zfill(2)

            elif self.data.index[i + 1].month != date.month != 12:
                # sell current position
                ticker_sell = current_pos.iloc[0]['ticker']
                # buy next contract
                ticker_buy = 'UC' + FutureCode((date.month+1) % 12 + 1).name + str(date.year - 2000 + (1 if (date.month+1) % 12 == 0 else 0)).zfill(2)
            else:
                #don't need to do anything unless current position is 0
                if current_pos.empty:
                    ticker_buy = 'UC' + FutureCode(date.month+1).name + str(date.year - 2000).zfill(2)

            if ticker_buy:
                fut = DataManager().load(ticker_buy)[ticker_buy]
                self.portfolio.add_order_future(date=date, ticker=ticker_buy, qty=nav / fut.get_close(date=date) / fut.m)

            if ticker_sell:
                qty = -current_pos.iloc[0]['qty']
                self.portfolio.add_order_future(date=date, ticker=ticker_sell, qty=qty)
        pass
