from functools import cache
from typing import Union

import pandas as pd
import numpy as np
import datetime as dt
import arcticdb as adb

from model.asset import Asset
from utils.pcalendar import CalendarType, Calendar
from model.future import Future

from core import const

class DataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        pass

    @cache
    def load(self, ticker: Union[list, str], begin: dt.datetime = None, end: dt.datetime = None) -> dict[str, Asset]:
        """
        Load data from database
        :param ticker:
        :param begin:
        :param end:
        :return: dictionary with each ticker and its data
        """
        if type(ticker) is str:
            ticker = [ticker]

        ac = adb.Arctic(const.ARTCIC_DB)
        lib = ac.get_library(const.LIBRARY_DATA)

        r = {}
        for t in ticker:
            if t[:2] == 'UC':
                r[t] = self.load_uc()[t]
            else:
                lib_data = lib.read(t)
                df = lib_data.data
                meta_data = lib_data.metadata
                df['ticker'] = t
                f = Future(ticker=t, calendar=CalendarType.B3, maturity=dt.datetime.max, m=330.0, min_lot=1, cost_bps=15 / 10000,
                           cost_unit=0.0, market_data=df, days2settle=1, metadata=meta_data)
                r[t] = f

        lib = None
        ac = None

        return r

    @cache
    def load_uc(self):
        code_future = pd.DataFrame.from_dict(
            [{'c': 'F', 'month': 1}, {'c': 'G', 'month': 2}, {'c': 'H', 'month': 3}, {'c': 'J', 'month': 4}, {'c': 'K', 'month': 5}, {'c': 'M', 'month': 6},
             {'c': 'N', 'month': 7}, {'c': 'Q', 'month': 8}, {'c': 'U', 'month': 9}, {'c': 'V', 'month': 10}, {'c': 'X', 'month': 11}, {'c': 'Z', 'month': 12}],
            orient='columns')

        path_b3 = 'd:\\OneDrive\\MarketData\\SistemaPregao\\'
        file_name = 'DOL.xlsx'
        df = pd.read_excel(path_b3 + file_name, engine='openpyxl')
        df['DATE'] = pd.to_datetime(df['DATE'])
        df['c'] = df['MATURITY_CODE'].str[0:1]
        df = df.merge(code_future, on='c')
        df['a'] = df['MATURITY_CODE'].str[1:3].astype(int) + 2000
        df['maturity'] = df['a'].astype(str) + '-' + df['month'].astype(str).str.zfill(2) + '-01'
        df['maturity'] = pd.to_datetime(df['maturity']).dt.date
        df = df.drop(['c', 'month', 'a'], axis=1)
        df = df[['DATE', 'CONTRACT', 'MATURITY_CODE', 'maturity', 'OPENING_PRICE', 'MINIMUM_PRICE', 'MAXIMUM_PRICE', 'SETTLEMENT_PRICE','TRADING_VOLUME']]

        bz = Calendar(calendar_type=CalendarType.BR)
        hol_bz = bz.holidays()

        df['maturity'] = np.busday_offset(df['maturity'].values.astype('datetime64[D]') - np.timedelta64(1, 'D'), offsets=1, holidays=hol_bz, roll='backward')
        df.columns = ['datetime', 'contract', 'maturity_code', 'maturity', 'open', 'low', 'high', 'close', 'volume']
        df['ticker'] = 'UC' + df['maturity_code']
        df = df.drop(labels=['contract', 'maturity_code'], axis=1)

        r = {}
        for t in df['ticker'].drop_duplicates():
            tmp = df.loc[df['ticker'] == t].set_index('datetime', drop=True)
            r[t] = Future(ticker=t, calendar=CalendarType.B3, maturity=tmp['maturity'].values[-1],
                          m=50.0, min_lot=1, cost_bps=1 / 10000, cost_unit=0.0, market_data=tmp, days2settle=1)

        return r