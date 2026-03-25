Backtester and NAV calculator

Strategy is called portfolio manager and has its own decision making data, unlike many other backtester around, with that is easier to make macro and cross asset strategies.

If the objective is to run a real portfolio just load the trades from somewhere and input then at each date.

How it works:
Portfolio manager has the logic of the trading and has a portfolio.
Portfolio calculates NAV, NAVPS and P&L everyday.

Tips:
Once method runs on the begining of the backtest and should be used to do a one time calculation and benefit from vectorized functions.

Still WIP:
* Currency conversions
* Extend to cash equities, options etc
* Add feature to enable strategy on strategy
* Add required fields / attributes / parameters
* Add log
* many more features