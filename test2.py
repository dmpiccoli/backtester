
import datetime as dt

from core.backtester import Backtester
from model.portfolio_manager.future_roll import FutureRoll
from utils.pcalendar import CalendarType

if __name__ == '__main__':
    print(dt.datetime.now())

    name = 'UC1'

    pm = FutureRoll.load(name)
    if pm is None:
        pm = FutureRoll(name=name, first_trade=dt.datetime(2007, 1, 2),
                      trade_calendar=CalendarType.B3, portfolio_calendar=CalendarType.BR)
    #update decision data
    pm.load_data()

    bt = Backtester(portfolio_manager=pm)
    bt.run(end_date=dt.datetime(2024,12,30), run_all=True)

    print(dt.datetime.now())
    pm.save()
    print(pm.portfolio.market_data)

    pm2 = Momentum.load(name)
    pm2.load_data(ticker)
    bt2 = Backtester(portfolio_manager=pm2)
    bt2.run(run_all=False)

    print(pm2.portfolio.market_data)
    pass
    # p = portfolio.Portfolio('teste', begin_date=dt.datetime(2022, 5, 31))

pass
