import datetime as dt
import numpy as np
import math

import pandas as pd
from data.data_manager import DataManager
from model.asset import Asset

from utils.pcalendar import Calendar, CalendarType


class Portfolio(Asset):
    """
    Portfolio class
    
    Base class to process portfolio results
    """
    begin_date: dt.datetime
    start_nav: float
    calendar: Calendar
    cash_index: str
    last_update: dt.datetime

    def __init__(self, name: str, begin_date: dt.datetime, start_nav: float = 100000000.0,
                 calendar_type: CalendarType = CalendarType.BR, cash_index: str = 'BZACCETP Index') -> None:

        self.ticker = name
        self.calendar = Calendar(calendar_type)
        self.begin_date = self.calendar.workday(begin_date + dt.timedelta(days=-1), bd=1)
        self.start_nav = start_nav
        d_1 = self.calendar.workday(self.begin_date, -1)
        self.last_update = d_1

        self.market_data = pd.DataFrame(data=[[start_nav, 0.0, 1.0, 0.0, 0.0]], index=[begin_date], columns=['NAV', 'cash', 'close', 'r', 'alpha'])
        self.positions:dict[dt.datetime, dict[str, dict]] = {begin_date: {}, d_1: {}}

        self.positions[begin_date]['future'] : dict = {}
        self.positions[d_1]['future']: dict = {}
        self.positions[begin_date]['strategy'] : dict = {}
        self.positions[d_1]['strategy']: dict = {}
        self.positions[begin_date]['provision'] : dict = {}
        self.positions[d_1]['provision']: dict = {}

        self.trades : dict[dt.datetime, dict[str, list]] = {begin_date: {}}
        self.trades[begin_date]['future'] = []

        self.cash_index = cash_index
        self.cash : dict[dt.datetime, float] = {begin_date: start_nav, d_1: 0.0}

    def get_data(self, date: dt.datetime) -> pd.DataFrame:
        """
        Get portfolio data for a specific date.
        
        Return empty dataframe if the date is not valid
        """
        if date == self.begin_date:
            return self.market_data.loc[self.market_data.index == date]
        else:
            d_1 = self.calendar.workday(date, -1)
            if d_1 in self.market_data.index:
                return self.market_data.loc[self.market_data.index == d_1]
            else:
                return pd.DataFrame(columns=['NAV', 'cash', 'close', 'r', 'alpha'])

    def get_positions_d1(self, date: dt.datetime) -> pd.DataFrame:
        """
        Get all open positions for D-1 of a specific date.

        Return empty dataframe if the date is not valid
        """
        if len(self.market_data.loc[self.market_data.index < date]['NAV']) > 0:
            nav = self.market_data.loc[self.market_data.index < date]['NAV'].values[-1]
            d_1 = self.market_data.loc[self.market_data.index < date]['NAV'].index[-1]
        else:
            return pd.DataFrame(columns=['ticker', 'qty', 'price', 'value', 'perc'])

        pos = pd.DataFrame(columns=['ticker', 'qty', 'price', 'value', 'perc'])
        if d_1 in self.positions:
            for p in self.positions[d_1]['future'].values():
                tmp = pd.DataFrame(columns=['ticker', 'qty', 'price', 'value', 'perc'],
                                   data=[[p['ticker'], p['qty'], p['price'], p['qty'] * p['m'] * p['price'], p['qty'] * p['m'] * p['price'] / nav]])
                if pos.empty:
                    pos = tmp
                else:
                    pos = pd.concat([pos, tmp])
        return pos

    def get_positions(self) -> pd.DataFrame:
        """
        Get all open positions for all dates.

        Return empty dataframe if the date is not valid
        """
        # if d_1 in self.market_data.index:
        #     nav = self.market_data.loc[self.market_data.index == d_1]['NAV'].values[0]
        # else:
        #     return pd.DataFrame(columns=['ticker', 'qty', 'value', 'perc'])

        pos = pd.DataFrame(columns=['datetime', 'ticker', 'qty', 'price', 'value'])
        for k1, p1 in self.positions.items():
            for p in self.positions[k1]['future'].values():
                tmp = pd.DataFrame(columns=['datetime', 'ticker', 'qty', 'price', 'value'],
                                   data=[[k1,p['ticker'], p['qty'], p['price'], p['qty'] * p['m'] * p['price']]])
                if pos.empty:
                    pos = tmp
                else:
                    pos = pd.concat([pos, tmp])

        pos = pos.set_index(keys='datetime', drop=True)
        pos = pos.merge(self.market_data[['NAV']], how='left', left_index=True, right_index=True)
        return pos

    def add_order_future(self, date: dt.datetime, ticker: str, qty: int, price: float = np.nan):
        #load metadata
        prices = DataManager().load(ticker)
        meta = prices[ticker]

        #min lot adjustment
        qty = round(qty / meta.min_lot)
        if date not in self.trades:
            self.trades[date] = {}
            self.trades[date]['future'] = []
        self.trades[date]['future'].append({'date': date, 'ticker': ticker, 'qty': qty, 'price': price})

    def process(self, end: dt.datetime) -> bool:
        if end < self.begin_date:
            return False

        # clear old data
        self.last_update = min(end, self.last_update)
        self.market_data = self.market_data[self.market_data.index <= self.last_update]

        process_date = self.calendar.workday(date=self.last_update, bd=1)
        while process_date <= end:
            #clear old positions, trades and cash
            self.positions = {k: v for k, v in self.positions.items() if k < process_date}
            self.trades = {k: v for k, v in self.trades.items() if k <= process_date}
            self.cash = {k: v for k, v in self.cash.items() if k < process_date}

            # get last nav
            if process_date == self.begin_date:
                # self.market_data = pd.DataFrame(data=[[self.start_nav, 0.0, 1.0, 0.0, 0.0]],
                #                                 index=[self.begin_date], columns=['NAV', 'cash', 'close', 'r', 'alpha'])
                last_nav = self.start_nav
            else:
                last_nav = self.market_data.loc[self.market_data.index == self.last_update, 'NAV'].values[0]

            #add new date
            self.positions[process_date] = {}
            self.positions[process_date]['future'] = {}
            self.positions[process_date]['provision'] = {}
            self.cash[process_date] = last_nav if process_date == self.begin_date else self.cash[max(self.cash.keys())]

            #totals
            total_pnl = 0.0
            total_cost_bps = 0.0
            total_cost_unit = 0.0
            try:
                ######################################## FUTURES ########################################
                #copy D-1 positions to new date
                for p in self.positions[self.last_update]['future'].values():
                    if p['qty'] != 0:
                        new_pos = {'ticker': p['ticker'], 'qty': p['qty'], 'price': 0.0, 'm': p['m'], 'pnl': 0.0}
                        fut = DataManager().load(ticker=p['ticker'])[p['ticker']]
                        new_pos['price'] = fut.get_close(date=process_date)
                        # Repeat price if it's nan
                        if math.isnan(new_pos['price']):
                            new_pos['price'] = p['price']
                        new_pos['pnl'] = new_pos['pnl'] + new_pos['qty'] * (new_pos['price'] - p['price']) * new_pos['m']
                        self.positions[process_date]['future'][new_pos['ticker']] = new_pos
                        total_pnl += new_pos['pnl']

                        # update provisions if it's different then 0
                        if new_pos['pnl'] != 0.0:
                            new_prov = {'ticker': new_pos['ticker'], 'maturity': fut.calendar.workday(process_date, fut.days2settle), 'value': new_pos['pnl']}
                            self.positions[process_date]['provision'][new_prov['ticker']] = new_prov

                #process trades
                if process_date in self.trades:
                    for t in self.trades[process_date]['future']:
                        #get metadata / last price for ticker
                        fut = DataManager().load(ticker=t['ticker'])[t['ticker']]

                        if t['ticker'] in self.positions[process_date]['future']:
                            new_pos = self.positions[process_date]['future'][t['ticker']]
                        else:
                            new_pos = {'ticker': t['ticker'], 'qty': 0, 'price': fut.get_close(date=process_date), 'm': fut.m, 'pnl': 0.0}

                        #update qty
                        new_pos['qty'] = new_pos['qty'] + t['qty']
                        #update dictionary of positions
                        self.positions[process_date]['future'][new_pos['ticker']] = new_pos
                        #Pnl and cost updates
                        cost_bps = abs(t['qty']) * new_pos['m'] * (new_pos['price'] if math.isnan(t['price']) else t['price']) * fut.cost_bps
                        cost_unit = abs(t['qty']) * new_pos['m'] * (new_pos['price'] if math.isnan(t['price']) else t['price']) * fut.cost_unit
                        pnl = 0.0 if math.isnan(t['price']) else (new_pos['price'] - t['price']) * t['qty'] * new_pos['m']
                        new_pos['pnl'] = new_pos['pnl'] + pnl - cost_bps - cost_unit

                        total_pnl += pnl - cost_bps - cost_unit
                        total_cost_bps += cost_bps
                        total_cost_unit += cost_unit

                        # update provisions
                        if new_pos['pnl'] != 0.0:
                            if t['ticker'] in self.positions[process_date]['provision']:
                                new_prov = self.positions[process_date]['provision'][t['ticker']]
                            else:
                                new_prov = {'ticker': new_pos['ticker'], 'maturity': self.calendar.workday(process_date, fut.days2settle), 'value': 0.0}
                            new_prov['value'] = new_prov['value'] + pnl - cost_bps - cost_unit
                            self.positions[process_date]['provision'][new_prov['ticker']] = new_prov

                # process yesterday cash
                for k in list(self.positions[self.last_update]['provision']):
                    if self.positions[self.last_update]['provision'][k]['maturity'] == process_date:
                        self.cash[process_date] = self.cash[process_date] + self.positions[self.last_update]['provision'][k]['value']
                    else:
                        new_prov = {'ticker': self.positions[self.last_update]['provision'][k]['ticker'], 'maturity': self.positions[self.last_update]['provision'][k]['maturity'], 'value': self.positions[self.last_update]['provision'][k]['value']}
                        self.positions[process_date]['provision'][self.positions[self.last_update]['provision'][k]['ticker']] = new_prov

                # process today cash
                for k in list(self.positions[process_date]['provision']):
                    if self.positions[process_date]['provision'][k]['maturity'] == process_date:
                        self.cash[process_date] = self.cash[process_date] + self.positions[end]['provision'][k]['value']
                        del self.positions[process_date]['provision'][k]
                    elif self.positions[process_date]['provision'][k]['value'] == 0.0:
                        del self.positions[process_date]['provision'][k]

                #update cash return
                c = DataManager().load(self.cash_index)[self.cash_index]
                total_pnl += self.cash[self.last_update] * (c.get_close(process_date) / c.get_close(self.last_update) - 1)
                self.cash[process_date] = self.cash[process_date] + self.cash[self.last_update] * (c.get_close(process_date) / c.get_close(self.last_update) - 1)

                # update values of portfolio

                self.market_data = pd.concat([self.market_data, pd.DataFrame(
                    data=[[last_nav + total_pnl, self.cash[process_date], 1.0, 0.0,
                           total_pnl / last_nav - (c.get_close(process_date) / c.get_close(self.last_update) - 1)]],
                    index=[process_date],
                    columns=['NAV', 'cash', 'close', 'r', 'alpha'])])

                # update NAV and NAVPS
                self.market_data['close'] = self.market_data['NAV'] / self.market_data.iloc[0]['NAV']
                self.market_data['r'] = self.market_data['close'].pct_change().fillna(0)

                self.last_update = process_date
                process_date = self.calendar.workday(date=self.last_update, bd=1)
            except Exception as e:
                raise(e)
                return False
        return True