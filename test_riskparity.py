
import datetime as dt

from core.portfolio_calculator import PortfolioCalculator
from model.portfolio.portfolio import Portfolio
from model.portfolio_manager.risk_parity import RiskParity
from utils.pcalendar import CalendarType

if __name__ == '__main__':
    print(dt.datetime.now())

    name = 'RiskParity'
    p = Portfolio(name=name, begin_date=dt.datetime(2006, 1, 2), currency='BRL', calendar=CalendarType.US, cash_index={'BRL':'BZACCETP Index', 'USD':'LD20TRUU Index'})
    pm = RiskParity(name=name, first_trade=dt.datetime(2006, 1, 2), trade_calendar=CalendarType.US, portfolio=p)
    #update decision data
    pm.load_data(tickers=['XLF US Equity', 'XLB US Equity', 'XLC US Equity',
                          'XLE US Equity','XLI US Equity', 'XLK US Equity', 'XLP US Equity',
                          'XLRE US Equity', 'XLU US Equity', 'XLV US Equity', 'XLY US Equity',
                          'IBOV Index', 'BZRFIMB5 Index', 'BZRFIB5+ Index', 'BZRFIRF1 Index', 'BZRFIR1+ Index', 'BZACCETP Index', 'LD20TRUU Index'])

    # pm.load_data(tickers=['SPY US Equity'])

    bt = PortfolioCalculator(portfolio_manager=pm)
    bt.run(end_date=dt.datetime(2026,3,31), run_all=True)

    print(dt.datetime.now())
    pm.save()
    pm.report()
    print(pm.portfolio.market_data)
    pass
    # p = portfolio.Portfolio('teste', begin_date=dt.datetime(2022, 5, 31))

pass
