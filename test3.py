
import datetime as dt

from core.portfolio_calculator import PortfolioCalculator
from model.portfolio_manager.risk_parity import RiskParity
from utils.pcalendar import CalendarType

if __name__ == '__main__':
    print(dt.datetime.now())

    name = 'RiskParity'

    pm = RiskParity(name=name, first_trade=dt.datetime(2007, 1, 2),
                      trade_calendar=CalendarType.B3, portfolio_calendar=CalendarType.BR)
    #update decision data
    pm.load_data(tickers=['XLF', 'XLB', 'XLC', 'XLE', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY'])

    bt = PortfolioCalculator(portfolio_manager=pm)
    bt.run(end_date=dt.datetime(2025,12,30), run_all=True)

    print(dt.datetime.now())
    pm.save()
    pm.report()
    print(pm.portfolio.market_data)
    pass
    # p = portfolio.Portfolio('teste', begin_date=dt.datetime(2022, 5, 31))

pass
