import datetime as dt
import numpy as np
import math

import pandas as pd
from data.data_manager import DataManager
from model.asset import Asset, AssetType

from utils.pcalendar import Calendar, CalendarType


class Portfolio(Asset):
    """
    Portfolio class
    
    Base class to process portfolio results
    """
    begin_date: dt.datetime
    start_nav: float
    calendar: Calendar
    cash_index: dict[str,str]
    last_update: dt.datetime

    positions: dict[dt.datetime, dict[str, dict]]
    trades: dict[dt.datetime, dict[str, list]]
    cash: dict[dt.datetime, dict[str, float]]

    def __init__(self, name: str, begin_date: dt.datetime, start_nav: float = 100000000.0, currency: str = 'BRL',
                 calendar: CalendarType = CalendarType.BR, cash_index: dict[str,str] = {'BRL':'BZACCETP Index', 'USD':'LD20TRUU Index'}) -> None:

        super().__init__(ticker=name, asset_type=AssetType.fund, currency=currency, calendar=calendar)

        self.begin_date = self.calendar.workday(begin_date + dt.timedelta(days=-1), bd=1)
        self.start_nav = start_nav
        d_1 = self.calendar.workday(self.begin_date, -1)
        self.last_update = d_1

        self.positions = {begin_date: {}, d_1: {}}

        self.positions[begin_date]['future'] : dict = {}
        self.positions[d_1]['future']: dict = {}
        self.positions[begin_date]['equity'] : dict = {}
        self.positions[d_1]['equity']: dict = {}
        self.positions[begin_date]['provision'] : dict = {}
        self.positions[d_1]['provision']: dict = {}

        self.trades = {begin_date: {}}
        self.trades[begin_date]['future'] = []
        self.trades[begin_date]['equity'] = []

        self.cash_index = cash_index
        self.cash = {begin_date: {self.currency: start_nav}, d_1: {self.currency: 0.0}}

        self.market_data = pd.DataFrame(index=[begin_date], columns=['NAV', 'close', 'r', 'alpha'] + ['cash_' + c for c in self.cash[begin_date].keys()],
                                             data=[[start_nav, 1.0, 0.0, 0.0] + [c for c in self.cash[begin_date].values()]])

    def get_data_by_date(self, date: dt.datetime) -> pd.DataFrame:
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

    def get_data(self, date: dt.datetime = None) -> pd.DataFrame:
        """
        Get portfolio data for a specific date or return all data.

        Return portfolio data
        """
        if date is None:
            return self.market_data
        else:
            return self.market_data.loc[self.market_data.index <= date]

    def get_positions_d1(self, date: dt.datetime) -> pd.DataFrame:
        """
        Get all open positions for D-1 of a specific date.

        Return empty dataframe if the date is not valid
        """
        if len(self.market_data.loc[self.market_data.index < date]['NAV']) > 0:
            nav = self.market_data.loc[self.market_data.index < date]['NAV'].values[-1]
            d_1 = self.market_data.loc[self.market_data.index < date]['NAV'].index[-1]
        else:
            return pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price', 'value', 'perc'])

        pos = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price', 'value', 'perc'])
        if d_1 in self.positions:
            for p in self.positions[d_1]['future'].values():
                tmp = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price', 'value', 'perc'],
                                   data=[[d_1, p['ticker'], 'future', p['qty'], p['price'], p['qty'] * p['m'] * p['price'], p['qty'] * p['m'] * p['price'] / nav]])
                if pos.empty:
                    pos = tmp
                else:
                    pos = pd.concat([pos, tmp])

            for p in self.positions[d_1]['equity'].values():
                tmp = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price', 'value', 'perc'],
                                   data=[[d_1, p['ticker'], 'future', p['qty'], p['price'], p['qty'] * p['m'] * p['price'], p['qty'] * p['m'] * p['price'] / nav]])
                if pos.empty:
                    pos = tmp
                else:
                    pos = pd.concat([pos, tmp])
        return pos

    def get_positions(self, date: dt.datetime) -> pd.DataFrame:
        """
        Get all open positions for a specific dates.

        Return empty dataframe if there is no positions
        """
        pos = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'asset', 'qty', 'price', 'value'])
        if date in self.positions:
            for p in self.positions[date]['future'].values():
                tmp = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price', 'value'],
                                   data=[[date, p['ticker'], 'future', p['qty'], p['price'], p['qty'] * p['m'] * p['price']]])
                if pos.empty:
                    pos = tmp
                else:
                    pos = pd.concat([pos, tmp])

            for p in self.positions[date]['equity'].values():
                tmp = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price', 'value'],
                                   data=[[date, p['ticker'], 'future', p['qty'], p['price'], p['qty'] * p['m'] * p['price']]])
                if pos.empty:
                    pos = tmp
                else:
                    pos = pd.concat([pos, tmp])
        pos = pos.set_index(keys='datetime', drop=True)
        return pos

    def get_positions(self) -> pd.DataFrame:
        """
        Get all open positions for all dates.

        Return empty dataframe if the date is not valid
        """
        pos = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price', 'value'])
        for k1, p1 in self.positions.items():
            for p in self.positions[k1]['future'].values():
                tmp = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price', 'value'],
                                   data=[[k1, p['ticker'], 'future', p['qty'], p['price'], p['qty'] * p['m'] * p['price']]])
                if pos.empty:
                    pos = tmp
                else:
                    pos = pd.concat([pos, tmp])

            for p in self.positions[k1]['equity'].values():
                tmp = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price', 'value'],
                                   data=[[k1, p['ticker'], 'equity', p['qty'], p['price'], p['qty'] * p['m'] * p['price']]])
                if pos.empty:
                    pos = tmp
                else:
                    pos = pd.concat([pos, tmp])
        if not pos.empty:
            pos = pos.set_index(keys='datetime', drop=True)
        return pos

    def get_trades(self) -> pd.DataFrame:
        """
        Get all trades for all dates.

        Return empty dataframe if there are no trades
        """
        trades = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price'])
        for k1, t1 in self.trades.items():
            if 'future' in self.trades[k1]:
                for t in self.trades[k1]['future']:
                    tmp = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price'],
                                       data=[[k1, t['ticker'], 'future', t['qty'], 'Settle' if math.isnan(t['price']) else t['price']]])
                    if trades.empty:
                        trades = tmp
                    else:
                        trades = pd.concat([trades, tmp])

            if 'equity' in self.trades[k1]:
                for t in self.trades[k1]['equity']:
                    tmp = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'qty', 'price'],
                                       data=[[k1, t['ticker'], 'future', t['qty'], 'Settle' if math.isnan(t['price']) else t['price']]])
                    if trades.empty:
                        trades = tmp
                    else:
                        trades = pd.concat([trades, tmp])

        if not trades.empty:
            trades = trades.set_index(keys='datetime', drop=True)
        return trades

    def get_provisions(self) -> pd.DataFrame:
        """
        Get all open provisions for all dates.

        Return empty dataframe if the date is not valid
        """
        pos = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'currency', 'value', 'fx'])
        for k1, p1 in self.positions.items():
            for p in self.positions[k1]['provision'].values():
                tmp = pd.DataFrame(columns=['datetime', 'ticker', 'asset', 'currency', 'value', 'fx'],
                                   data=[[k1, p['ticker'], 'provision', p['currency'], p['value'], p['c']]])
                if pos.empty:
                    pos = tmp
                else:
                    pos = pd.concat([pos, tmp])
        if not pos.empty:
            pos = pos.set_index(keys='datetime', drop=True)
        return pos

    def get_cash(self):
        """
        Get cash positions for all dates.

        Return empty dataframe if there are no cash positions
        """
        cash = pd.DataFrame(columns=['datetime', 'currency', 'asset', 'value'])
        for k1, c1 in self.cash.items():
            for k2, c2 in self.cash[k1].items():
                tmp = pd.DataFrame(columns=['datetime', 'currency', 'asset', 'value'],
                                   data=[[k1, k2, 'cash', c2]])
                if cash.empty:
                    cash = tmp
                else:
                    cash = pd.concat([cash, tmp])
        if not cash.empty:
            cash = cash.set_index(keys='datetime', drop=True)
        return cash

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

    def add_order_equity(self, date: dt.datetime, ticker: str, qty: int, price: float = np.nan):
        #load metadata
        prices = DataManager().load(ticker)
        meta = prices[ticker]

        #min lot adjustment
        qty = round(qty / meta.min_lot)
        if date not in self.trades:
            self.trades[date] = {}
            self.trades[date]['equity'] = []
        self.trades[date]['equity'].append({'date': date, 'ticker': ticker, 'qty': qty, 'price': price})

    def add_order_equity_perc(self, date: dt.datetime, ticker: str, perc: float):
        # get current nav
        nav = self.get_data()
        nav = nav.loc[nav.index < date, 'NAV']  # get D-1
        if nav.empty:
            nav = self.start_nav
        else:
            nav = nav.values[-1]

        # load metadata
        eq = DataManager().load(ticker)[ticker]
        d_1 = eq.market_data.index[eq.market_data.index < date].max()
        p = eq.get_close(date=d_1)

        if eq.currency != self.currency:
            c = DataManager().load(ticker=eq.currency + self.currency + ' Curncy')[eq.currency + self.currency + ' Curncy']
            c = c.get_close(date=d_1)
        else:
            c = 1.0

        # get current position
        current_pos = self.get_positions_d1(date)
        if current_pos.empty:
            old_qty = 0
        else:
            current_pos = current_pos.loc[current_pos['ticker'] == ticker]
            if current_pos.empty:
                old_qty = 0
            else:
                old_qty = current_pos['qty'].values[0]
        # min lot adjustment
        qty = math.trunc(nav * perc / p / c / eq.min_lot) * eq.min_lot
        if date not in self.trades:
            self.trades[date] = {}
            self.trades[date]['equity'] = []
        self.trades[date]['equity'].append({'date': date, 'ticker': ticker, 'qty': qty - old_qty, 'price': np.nan})

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
                last_nav = self.start_nav
            else:
                last_nav = self.market_data.loc[self.market_data.index == self.last_update, 'NAV'].values[0]

            #add new date
            self.positions[process_date] = {}
            self.positions[process_date]['future'] = {}
            self.positions[process_date]['equity'] = {}
            self.positions[process_date]['provision'] = {}
            self.cash[process_date] = { self.currency: last_nav if process_date == self.begin_date else self.cash[max(self.cash.keys())][self.currency] }

            try:
                # region Futures
                #copy D-1 positions to new date
                for p in self.positions[self.last_update]['future'].values():
                    if p['qty'] != 0:
                        # Load instrument data
                        fut = DataManager().load(ticker=p['ticker'])[p['ticker']]
                        # Convert P&L if quote currency is different from settlement currency
                        if fut.settlement_currency != fut.settlement_currency:
                            c = DataManager().load(ticker=fut.currency + fut.settlement_currency + ' Curncy')[fut.currency + fut.settlement_currency + ' Curncy']
                            c = c.get_close(date=process_date)
                        else:
                            c = 1.0

                        # create new position
                        new_pos = {'ticker': p['ticker'], 'currency': p['currency'], 'settlement_currency': p['settlement_currency'], 'qty': p['qty'],
                                   'price': fut.get_close(date=process_date), 'm': p['m'], 'pnl': 0.0, 'c': c}

                        # Repeat price if it's nan
                        if math.isnan(new_pos['price']):
                            new_pos['price'] = p['price']

                        new_pos['pnl'] = new_pos['pnl'] + (new_pos['qty'] * (new_pos['price'] - p['price']) * new_pos['m']) * new_pos['c']
                        self.positions[process_date]['future'][new_pos['ticker']] = new_pos

                        # Update provisions if it's different then 0
                        if new_pos['pnl'] != 0.0:
                            new_prov = {'ticker': new_pos['ticker'], 'maturity': fut.calendar.workday(process_date, fut.days2settle),
                                        'currency':fut.settlement_currency, 'value': new_pos['pnl'], 'c':c}
                            self.positions[process_date]['provision'][new_prov['ticker']] = new_prov

                #process trades
                if process_date in self.trades and 'future' in self.trades[process_date]:
                    for t in self.trades[process_date]['future']:
                        # Get metadata / last price for ticker
                        fut = DataManager().load(ticker=t['ticker'])[t['ticker']]

                        # Get currency to convert P&L if quote currency is different from settlement currency
                        if fut.settlement_currency != fut.settlement_currency:
                            c = DataManager().load(ticker=fut.currency + fut.settlement_currency + ' Curncy')[fut.currency + fut.settlement_currency + ' Curncy']
                            c = c.get_close(date=process_date)
                        else:
                            c = 1.0

                        # Check if already have a position
                        if t['ticker'] in self.positions[process_date]['future']:
                            new_pos = self.positions[process_date]['future'][t['ticker']]
                        else:
                            new_pos = {'ticker': t['ticker'], 'currency': fut.currency, 'settlement_currency': fut.settlement_currency,
                                       'qty': 0, 'price': fut.get_close(date=process_date), 'm': fut.m, 'pnl': 0.0, 'c': c}

                        # update qty
                        new_pos['qty'] = new_pos['qty'] + t['qty']
                        # update dictionary of positions
                        self.positions[process_date]['future'][new_pos['ticker']] = new_pos
                        # Pnl and cost updates (if price is nan then trade at settle)
                        cost_bps = abs(t['qty']) * new_pos['m'] * (new_pos['price'] if math.isnan(t['price']) else t['price']) * fut.cost_bps * new_pos['c']
                        cost_unit = abs(t['qty']) * new_pos['m'] * (new_pos['price'] if math.isnan(t['price']) else t['price']) * fut.cost_unit * new_pos['c']
                        pnl = 0.0 if math.isnan(t['price']) else (new_pos['price'] - t['price']) * t['qty'] * new_pos['m'] * new_pos['c']
                        new_pos['pnl'] = new_pos['pnl'] + (pnl - cost_bps - cost_unit) * new_pos['c']

                        # update provisions
                        if new_pos['pnl'] != 0.0:
                            if t['ticker'] in self.positions[process_date]['provision']:
                                new_prov = self.positions[process_date]['provision'][t['ticker']]
                            else:
                                new_prov = {'ticker': new_pos['ticker'], 'maturity': self.calendar.workday(process_date, fut.days2settle),
                                            'currency': fut.settlement_currency, 'value': 0.0, 'c': new_pos['c']}
                            new_prov['value'] = new_prov['value'] + pnl - cost_bps - cost_unit
                            self.positions[process_date]['provision'][new_prov['ticker']] = new_prov
                # endregion Futures
                # region Equities

                # TODO process events

                # copy D-1 positions to new date
                for p in self.positions[self.last_update]['equity'].values():
                    if p['qty'] != 0:
                        # Load instrument data
                        eq = DataManager().load(ticker=p['ticker'])[p['ticker']]
                        # Convert P&L if quote currency is different from settlement currency
                        if eq.settlement_currency != eq.settlement_currency:
                            c = DataManager().load(ticker=eq.currency + eq.settlement_currency + ' Curncy')[eq.currency + eq.settlement_currency + ' Curncy']
                            c = c.get_close(date=process_date)
                        else:
                            c = 1.0

                        # create new position
                        new_pos = {'ticker': p['ticker'], 'currency': p['currency'], 'settlement_currency': p['settlement_currency'],
                                   'qty': p['qty'], 'price': eq.get_close(date=process_date), 'm': p['m'], 'pnl': 0.0, 'c': c}

                        # Repeat price if it's nan
                        if math.isnan(new_pos['price']):
                            new_pos['price'] = p['price']

                        new_pos['pnl'] = new_pos['pnl'] + (new_pos['qty'] * (new_pos['price'] - p['price']) * new_pos['m']) * new_pos['c']
                        self.positions[process_date]['equity'][new_pos['ticker']] = new_pos

                # process trades
                if process_date in self.trades and 'equity' in self.trades[process_date]:
                    for t in self.trades[process_date]['equity']:
                        # Get metadata / last price for ticker
                        eq = DataManager().load(ticker=t['ticker'])[t['ticker']]

                        # Get currency to convert P&L if quote currency is different from settlement currency
                        if eq.currency != eq.settlement_currency:
                            c = DataManager().load(ticker=eq.currency + eq.settlement_currency + ' Curncy')[eq.currency + eq.settlement_currency + ' Curncy']
                            c = c.get_close(date=process_date)
                        else:
                            c = 1.0

                        # Check if already have a position
                        if t['ticker'] in self.positions[process_date]['equity']:
                            new_pos = self.positions[process_date]['equity'][t['ticker']]
                        else:
                            new_pos = {'ticker': t['ticker'], 'currency': eq.currency, 'settlement_currency': eq.settlement_currency,
                                       'qty': 0, 'price': eq.get_close(date=process_date), 'm': eq.m, 'pnl': 0.0, 'c': c}

                        # update qty
                        new_pos['qty'] = new_pos['qty'] + t['qty']
                        # update dictionary of positions
                        self.positions[process_date]['equity'][new_pos['ticker']] = new_pos
                        # Pnl and cost updates (if price is nan then trade at settle)
                        cost_bps = abs(t['qty']) * new_pos['m'] * (new_pos['price'] if math.isnan(t['price']) else t['price']) * eq.cost_bps * new_pos['c']
                        cost_unit = abs(t['qty']) * new_pos['m'] * (new_pos['price'] if math.isnan(t['price']) else t['price']) * eq.cost_unit * new_pos['c']
                        pnl = 0.0 if math.isnan(t['price']) else (new_pos['price'] - t['price']) * t['qty'] * new_pos['m'] * new_pos['c']
                        new_pos['pnl'] = new_pos['pnl'] + (pnl - cost_bps - cost_unit) * new_pos['c']

                        # update provisions
                        if t['ticker'] in self.positions[process_date]['provision']:
                            new_prov = self.positions[process_date]['provision'][t['ticker']]
                        else:
                            new_prov = {'ticker': new_pos['ticker'], 'maturity': self.calendar.workday(process_date, eq.days2settle),
                                        'currency': eq.settlement_currency, 'value': 0.0, 'c': new_pos['c']}
                        new_prov['value'] = new_prov['value'] - cost_bps - cost_unit \
                                             - t['qty'] * new_pos['m'] * (new_pos['price'] if math.isnan(t['price']) else t['price']) * c
                        self.positions[process_date]['provision'][new_prov['ticker']] = new_prov
                # endregion Equities
                # region Provision
                # process yesterday provisions
                for k in list(self.positions[self.last_update]['provision']):
                    if self.positions[self.last_update]['provision'][k]['maturity'] == process_date:
                        curr_prov = self.positions[self.last_update]['provision'][k]['currency']

                        # Get currency to convert P&L if quote currency is different from settlement currency
                        if curr_prov != self.currency:
                            c = DataManager().load(ticker=curr_prov + self.currency + ' Curncy')[curr_prov + self.currency + ' Curncy']
                            c = c.get_close(date=process_date)
                        else:
                            c = 1.0
                        self.cash[process_date][self.currency] += self.positions[self.last_update]['provision'][k]['value'] * c
                    else:
                        new_prov = {'ticker': self.positions[self.last_update]['provision'][k]['ticker'],
                                    'maturity': self.positions[self.last_update]['provision'][k]['maturity'],
                                    'currency': self.positions[self.last_update]['provision'][k]['currency'],
                                    'value': self.positions[self.last_update]['provision'][k]['value']}
                        self.positions[process_date]['provision'][self.positions[self.last_update]['provision'][k]['ticker']] = new_prov

                # process today provisions
                for k in list(self.positions[process_date]['provision']):
                    if self.positions[process_date]['provision'][k]['maturity'] == process_date:
                        curr_prov = self.positions[process_date]['provision'][k]['currency']
                        # Get currency to convert P&L if quote currency is different from settlement currency
                        if curr_prov != self.currency:
                            c = DataManager().load(ticker=curr_prov + self.currency + ' Curncy')[curr_prov + self.currency + ' Curncy']
                            c = c.get_close(date=process_date)
                        else:
                            c = 1.0
                        self.cash[process_date][self.currency] += self.positions[process_date]['provision'][k]['value'] * c
                        del self.positions[process_date]['provision'][k]
                    elif self.positions[process_date]['provision'][k]['value'] == 0.0:
                        del self.positions[process_date]['provision'][k]
                # endregion Provision
                #region Cash
                #update cash return
                for k, i in self.cash[process_date].items():
                    q = DataManager().load(self.cash_index[k])[self.cash_index[k]]
                    self.cash[process_date][k] = self.cash[process_date][k] * (q.get_close(process_date) / q.get_close(self.last_update))
                # endregion Cash
                # update values of portfolio
                total_nav = 0.0
                for k, p in self.positions[process_date].items():
                    if k != 'future':
                        for i in p.values():
                            # Convert P&L if settlement currency is different from portfolio currency
                            if i['currency'] != self.currency:
                                c = DataManager().load(ticker=i['currency'] + self.currency + ' Curncy')[i['currency'] + self.currency + ' Curncy']
                                c = c.get_close(date=process_date)
                            else:
                                c = 1.0

                            if k == 'provision':
                                total_nav += i['value'] * c
                            else:
                                total_nav += i['qty'] * i['price'] * i['m'] * c
                for k, p in self.cash[process_date].items():
                    # Convert P&L if settlement currency is different from portfolio currency
                    if k != self.currency:
                        c = DataManager().load(ticker=k + self.currency + ' Curncy')[k + self.currency + ' Curncy']
                        c = c.get_close(date=process_date)
                    else:
                        c = 1.0
                    total_nav += p * c

                q = DataManager().load(self.cash_index[self.currency])[self.cash_index[self.currency]]
                self.market_data = pd.concat([self.market_data,
                                              pd.DataFrame(index=[process_date], columns=['NAV', 'close', 'r', 'alpha'] + ['cash_' + c for c in self.cash[process_date].keys()],
                                             data=[[total_nav, 1.0, 0.0,
                                                    total_nav / last_nav - q.get_close(process_date) / q.get_close(max(self.last_update, self.begin_date))] +
                                                                 [c for c in self.cash[process_date].values()]])])

                # update NAV and NAVPS
                self.market_data['close'] = self.market_data['NAV'] / self.market_data.iloc[0]['NAV']
                self.market_data['r'] = self.market_data['close'].pct_change().fillna(0)

                self.last_update = process_date
                # print('Processed: ' + process_date.strftime('%Y-%m-%d'))
                process_date = self.calendar.workday(date=self.last_update, bd=1)
            except Exception as e:
                raise(e)
                return False
        return True