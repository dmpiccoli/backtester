
import datetime as dt

from core.portfolio_calculator import PortfolioCalculator
from model.portfolio.portfolio import Portfolio
from model.portfolio_manager.future_roll import FutureRoll
from utils.pcalendar import CalendarType

if __name__ == '__main__':
    print(dt.datetime.now())

    name = 'UC1'
    port = Portfolio(name=name, begin_date=dt.datetime(2006, 1, 3), calendar=CalendarType.BR, currency='BRL', cash_index={'BRL': 'CONST_BRL'})
    pm = FutureRoll(name=name, first_trade=dt.datetime(2007, 1, 2), trade_calendar=CalendarType.B3, portfolio_calendar=CalendarType.BR, portfolio=port)
    #update decision data
    pm.ticker_root = 'UC'
    pm.load_data()

    bt = PortfolioCalculator(portfolio_manager=pm)
    bt.run(end_date=dt.datetime(2024,12,30), run_all=True)

    print(dt.datetime.now())
    pm.save()
    pm.report()
    print(pm.portfolio.market_data)
    pass
    # p = portfolio.Portfolio('teste', begin_date=dt.datetime(2022, 5, 31))

pass
