
import datetime as dt

from core.portfolio_calculator import PortfolioCalculator
from model.portfolio.portfolio import Portfolio
from utils.pcalendar import CalendarType
from model.portfolio_manager.rsi import Rsi

if __name__ == '__main__':
    print(dt.datetime.now())

    name = 'RSI3_SPY'
    ticker = 'SPY US Equity'

    port = Portfolio(name=name, begin_date=dt.datetime(2006, 1, 3), calendar=CalendarType.US,
                     currency='USD', cash_index={'USD': 'LD20TRUU Index'})

    pm = Rsi(name=name, w=3, first_trade=dt.datetime(2007, 1, 2), trade_calendar=CalendarType.US,
             portfolio_calendar=CalendarType.US, portfolio=port)

    pm.load_data(ticker)
    bt = PortfolioCalculator(portfolio_manager=pm)
    bt.run(end_date=dt.datetime(2026,8,31), run_all=True)
    pm.report()
    print(dt.datetime.now())

pass
