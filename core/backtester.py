import datetime as dt
import warnings

from model.portfolio.portfolio import Portfolio
from model.portfolio_manager.portfolio_manager import PortfolioManager
from utils.pcalendar import Calendar, CalendarType


class Backtester:
    """
    Main engine for running historical backtests on a portfolio.

    Attributes:
        portfolio_manager (PortfolioManager): Object managing the portfolio logic and state.
    """
    portfolio_manager: PortfolioManager
    portfolio: Portfolio

    def __init__(self, portfolio_manager: PortfolioManager) -> None:
        """
        Initialize the core with a given PortfolioManager.

        Args:
            portfolio_manager (PortfolioManager): Instance managing the portfolio.
        """
        self.portfolio_manager = portfolio_manager
        self.portfolio = portfolio_manager.portfolio

    def run(self, end_date: dt.datetime = dt.datetime.today(), run_all:bool = True) -> None:
        """
        Run the backtest from the portfolio's begin_date until a specified end_date.

        This method first executes a one-time setup via `once()`, and then simulates
        trading day-by-day, filtering by business days from the calendar.

        Args:
            end_date (datetime): The last date to run the backtest. Defaults to today.
            run_all (bool): forces to run all the backtest otherwise continue from it stopped
        """
        self.portfolio_manager.once()

        if self.portfolio_manager.first_trade < self.portfolio_manager.portfolio.begin_date:
            warnings.warn("Trying to start trade before the portfolio exists")

        no_calendar = Calendar(CalendarType.NOCAL)
        if run_all:
            current_date = self.portfolio.begin_date
        else:
            current_date = self.portfolio.last_update
            current_date = no_calendar.workday(date=current_date, bd=1)

        while current_date <= end_date:
            if self.portfolio_manager.calendar.is_business_day(current_date):
                self.portfolio_manager.next(current_date)

            if self.portfolio.calendar.is_business_day(current_date):
                self.portfolio.process(current_date)
            current_date = no_calendar.workday(date=current_date, bd=1)