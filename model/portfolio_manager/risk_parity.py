import datetime as dt

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf

from data.data_manager import DataManager
from model.future import FutureCode
from utils.pcalendar import CalendarType
from model.portfolio.portfolio import Portfolio
from model.portfolio_manager.portfolio_manager import PortfolioManager

def _calculate_portfolio_var(w, V):
    # function that calculates portfolio risk
    w = np.matrix(w)
    return (w * V * w.T)[0, 0]

def _calculate_risk_contribution(w, V):
    # function that calculates asset contribution to total risk
    w = np.matrix(w)
    sigma = np.sqrt(_calculate_portfolio_var(w, V))
    # Marginal Risk Contribution
    MRC = V * w.T
    # Risk Contribution
    RC = np.multiply(MRC, w.T) / sigma
    return RC

def _risk_budget_objective(x, pars):
    # calculate portfolio risk
    V = pars[0]  # covariance table
    x_t = pars[1]  # risk target in percent of portfolio risk
    sig_p = np.sqrt(_calculate_portfolio_var(x, V))  # portfolio sigma
    risk_target = np.asmatrix(np.multiply(sig_p, x_t))
    asset_RC = _calculate_risk_contribution(x, V)
    return sum(np.square(asset_RC - risk_target.T))  # sum of squared error

def _total_weight_constraint(x):
    return np.sum(x) - 1.0

def _long_only_constraint(x):
    return x




class RiskParity(PortfolioManager):
    def __init__(self, name: str, first_trade: dt.datetime = dt.datetime(2000, 1, 1), trade_calendar: CalendarType = CalendarType.B3,
                 portfolio_calendar: CalendarType = CalendarType.BR, portfolio: Portfolio = None) -> None:

        super().__init__(name, first_trade, trade_calendar, portfolio_calendar, portfolio)
        pass

    def load_data(self, tickers:list, update=False):
        data = DataManager().load(ticker=tickers)
        df_ret = pd.DataFrame()
        for k, v in data.items():
            tmp = v.market_data
            df_ret = pd.concat([df_ret, tmp.reset_index()[['date', 'ticker', 'close']]])
        df_ret = df_ret.pivot(index='date', columns='ticker', values='close')
        df_ret = np.log(df_ret).diff()
        for c in df_ret.columns:
            if c in ['IBOV Index', 'BZRFIMB5 Index', 'BZRFIB5+ Index', 'BZRFIRF1 Index', 'BZRFIR1+ Index']:
                df_ret[c] = df_ret[c] - df_ret['BZACCETP Index']
            elif c[-9:] == 'US Equity':
                df_ret[c] = df_ret[c] - df_ret['LD20TRUU Index']

        df_ret = df_ret.drop(['BZACCETP Index', 'LD20TRUU Index'], axis=1)
        df_ret = df_ret.fillna(0)
        df_cov = pd.DataFrame()

        lw = LedoitWolf()
        for i in range(2, df_ret.shape[0] - 504):
            window_data = df_ret.iloc[i:i + 504]
            #exclude assets that have all zeros
            cov_assets = window_data.columns[~(window_data == 0.0).all(axis=0)]
            window_data = window_data[cov_assets]
            lw.fit(window_data.values)
            if df_cov.empty:
                df_cov = pd.DataFrame(index=pd.MultiIndex.from_product([[window_data.index[-1]], cov_assets]), columns=cov_assets, data=lw.covariance_)
            else:
                df_cov = pd.concat([df_cov, pd.DataFrame(index=pd.MultiIndex.from_product([[window_data.index[-1]], cov_assets]),
                                     columns=cov_assets, data=lw.covariance_)])

        self.data = df_cov
        pass

    def once(self):
        pass

    def next(self, date: dt.datetime):
        #get cov data
        df_cov = self.data[self.data.index.get_level_values(0) < date]

        port_data = self.portfolio.get_data()
        port_data = port_data[port_data.index < date]
        #rebal every 1st day of the month
        if port_data.empty or (df_cov.index.get_level_values(0).max().month != date.month and date in self.data.index.get_level_values(0)):
            df_cov = self.data[self.data.index.get_level_values(0) == date]

            selected_assets = df_cov.sum(axis=0)
            selected_assets = selected_assets.loc[selected_assets != 0.0].index

            df_cov = df_cov[df_cov.index.get_level_values(1).isin(selected_assets)][selected_assets]
            x = [1 / len(selected_assets)] * len(selected_assets)  # your risk budget percent of total portfolio risk (equal risk)
            cons = ({'type': 'eq', 'fun': _total_weight_constraint}, {'type': 'ineq', 'fun': _long_only_constraint})
            bounds = []
            for c in df_cov.columns:
                if c == 'IBOV Index':
                    bounds.append((0.2, 0.2))
                elif c == 'BZRFIB5 Index':
                    bounds.append((0.1, 0.1))
                elif c == 'BZRFIB5+ Index':
                    bounds.append((0.1, 0.1))
                elif c == 'BZRFIRF1 Index':
                    bounds.append((0.1, 0.1))
                elif c == 'BZRFIR1+ Index':
                    bounds.append((0.3, 0.3))
                else:
                    bounds.append((0.01, 0.15))
            res = minimize(_risk_budget_objective, x, args=[df_cov.values, x], method='SLSQP', constraints=cons, tol=1e-12, bounds=bounds, options={'disp': False})
            df_pos = pd.DataFrame(index=[date], columns=df_cov.columns, data=[res.x])

            for c in df_pos.columns:
                #if c not in ['IBOV Index', 'BZRFIMB5 Index', 'BZRFIB5+ Index', 'BZRFIRF1 Index', 'BZRFIR1+ Index']:
                self.portfolio.add_order_equity_perc(date=date, ticker=c, perc=df_pos[c].values[0])

        pass
