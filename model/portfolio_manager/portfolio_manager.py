import datetime as dt
import os
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd
import pickle

import quantstats as qs
from benchmarks.common import download_file

from core import const
from utils.pcalendar import Calendar, CalendarType
from model.portfolio.portfolio import Portfolio


class PortfolioManager(ABC):
    """
    Portfolio Manager Class. Is the same as strategy. 
    
    Should contain all the decision making process for the strategy. The data is independent from the portfolio
    """
    name: str
    calendar: Calendar
    portfolio: Portfolio
    first_trade: dt.datetime
    data: Any

    def __init__(self, name: str, first_trade: dt.datetime = dt.datetime(2000, 1, 1), trade_calendar: CalendarType = CalendarType.B3,
                 portfolio_calendar: CalendarType = CalendarType.BR, portfolio: Portfolio = None) -> None:

        self.name = name
        self.calendar = Calendar(trade_calendar)
        self.first_trade = self.calendar.workday(first_trade + dt.timedelta(days=1), -1)
        if portfolio is None:
            self.portfolio = Portfolio(name=name, begin_date=first_trade, calendar=portfolio_calendar)
        else:
            self.portfolio = portfolio

    @abstractmethod
    def load_data(self, update=False):
        """
        Load decision data
        :return:
        """

    @abstractmethod
    def once(self):
        """
        Run once to create allocations
        
        Should only be used in backtest
        """
        pass

    @abstractmethod
    def next(self, date: dt.datetime, data: pd.DataFrame):
        """
        Run every time period to decide what to do
        
        Watch out for look ahead bias
        """
        pass

    def save(self) -> bool:
        """
        Save portfolio manager and portfolio state to be able to continue later
        :return:
            bool
        """
        try:
            with open(const.MODEL_PATH + self.name + '.pkl', 'wb') as file:
                pickle.dump(self, file)
            return True
        except Exception as e:
            raise e

    @staticmethod
    def load(name: str) -> PortfolioManager:
        """
        Load portfolio manager and portfolio state
        :return: Portfolio manager object
        """
        try:
            if os.path.exists(const.MODEL_PATH + name + '.pkl'):
                with open(const.MODEL_PATH + name + '.pkl', 'rb') as file:
                    return pickle.load(file)
            else:
                return None
        except Exception as e:
            raise e

    def process_portfolio(self, end: dt.datetime) -> bool:
        return self.portfolio.process(end)

    def report(self) -> None:
        qs.reports.html(returns=self.portfolio.market_data.alpha, output=const.MODEL_PATH + self.name + '.html',
                        download_filename=const.MODEL_PATH + self.name + '.html')

        excel_writer = pd.ExcelWriter(const.MODEL_PATH + self.name + '.xlsx')
        self.portfolio.get_positions().to_excel(excel_writer=excel_writer, sheet_name='positions')
        self.portfolio.market_data.to_excel(excel_writer=excel_writer, sheet_name='data')
        self.portfolio.get_trades().to_excel(excel_writer=excel_writer, sheet_name='trades')
        excel_writer.close()
