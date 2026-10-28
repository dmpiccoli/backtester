import datetime as dt

import pandas as pd

from data.data_manager import DataManager
from model.future import FutureCode, Future
from utils.pcalendar import CalendarType
from model.portfolio.portfolio import Portfolio
from model.portfolio_manager.portfolio_manager import PortfolioManager


class FutureRoll(PortfolioManager):
    def __init__(self, name: str, first_trade: dt.datetime = dt.datetime(2000, 1, 1), trade_calendar: CalendarType = CalendarType.B3,
                 portfolio_calendar: CalendarType = CalendarType.BR, portfolio: Portfolio | None = None) -> None:

        super().__init__(name, first_trade, trade_calendar, portfolio_calendar, portfolio)
        self.ticker_root = None

    def load_data(self):
        tickers = DataManager().search_ticker(self.ticker_root)
        if self.ticker_root + '1 Curncy' in tickers:
            tickers.remove(self.ticker_root + '1 Curncy')

        futures = DataManager().load(tickers)
        df = pd.DataFrame()
        df_first_notice = pd.DataFrame()

        for k, f in futures.items():
            df = pd.concat(objs=[df, f.market_data.reset_index()[['datetime', 'ticker', 'close']]], axis=0)
            df_first_notice = pd.concat(objs=[df_first_notice, pd.DataFrame.from_dict({'ticker':[k], 'first_notice':[f.first_notice]})], axis=0)

        df = df.pivot(index='datetime', columns='ticker', values='close')
        self.data = {'prices': df, 'first_notice':df_first_notice}
        pass

    def once(self):
        pass

    def next(self, date: dt.datetime):
        current_port = self.portfolio.get_data_by_date(date)
        nav = current_port.iat[0, current_port.columns.get_loc('NAV')]
        current_pos = self.portfolio.get_positions_d1(date)

        ticker_buy = None
        ticker_sell = None

        if date in self.data['prices'].index:
            df_notice = self.data['first_notice']
            df = self.data['prices']

            i = self.data['prices'].index.get_loc(date)
            first_notice = df_notice.loc[df_notice['first_notice'] == df_notice.loc[df_notice['first_notice'] > date]['first_notice'].min(), 'first_notice'].values[0]

            if current_pos.empty:
                ticker_buy = df_notice.loc[df_notice['first_notice'] == df_notice.loc[df_notice['first_notice'] > date]['first_notice'].min(), 'ticker'].values[0]
            elif self.calendar.networkdays(date, pd.to_datetime(first_notice)) <= 1:
                ticker_sell = current_pos.iloc[0]['ticker']
                new_notice = df_notice.loc[df_notice['first_notice'] > df_notice.loc[df_notice['ticker'] == ticker_sell]['first_notice'].values[0]]['first_notice'].min()
                ticker_buy = df_notice.loc[df_notice['first_notice'] == new_notice, 'ticker'].values[0]

            if ticker_buy:
                fut = DataManager().load(ticker_buy)[ticker_buy]
                self.portfolio.add_order(date=date, ticker=ticker_buy, qty=nav / fut.get_close(date=date) / fut.m)

            if ticker_sell:
                qty = -current_pos.iloc[0]['qty']
                self.portfolio.add_order(date=date, ticker=ticker_sell, qty=qty)
        pass
