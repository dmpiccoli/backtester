from datetime import timedelta
import datetime as dt
import numpy as np
import enum

(MON, TUE, WED, THU, FRI, SAT, SUN) = range(7)
(BR, B3, US) = range(3)


class CalendarType(enum.Enum):
    BR = 0
    B3 = 1
    US = 2
    NOCAL = 3


class Calendar:
    """
    Calendar class
    Calculates business days and day counting

    Returns:
        Calendar object
    """
    calendarType: CalendarType

    def __init__(self, calendar_type: 'CalendarType' = CalendarType.BR) -> None:
        self.calendarType = calendar_type

    def holidays(self):
        hol = []
        begin = dt.datetime(1990, 1, 1)
        end = dt.datetime(2070, 12, 31)
        if self.calendarType == CalendarType.BR:
            while begin <= end:
                if not self.__is_business_day_brazil(begin) and begin.weekday != SAT and begin.weekday != SUN:
                    hol.append(begin)
                begin = begin + dt.timedelta(days=1)
        elif self.calendarType == CalendarType.B3:
            while begin <= end:
                if not self.__is_business_day_b3(begin) and begin.weekday != SAT and begin.weekday != SUN:
                    hol.append(begin)
                begin = begin + dt.timedelta(days=1)
        elif self.calendarType == CalendarType.US:
            while begin <= end:
                if not self.__is_business_day_us_settle(begin) and begin.weekday != SAT and begin.weekday != SUN:
                    hol.append(begin)
                begin = begin + dt.timedelta(days=1)
        return np.array(hol, dtype='datetime64[D]')

    def __easter_monday(self, y):
        easter = [98, 90, 103, 95, 114, 106, 91, 111, 102,  # 1901-1909
                  87, 107, 99, 83, 103, 95, 115, 99, 91, 111,  # 1910-1919
                  96, 87, 107, 92, 112, 103, 95, 108, 100, 91,  # 1920-1929
                  111, 96, 88, 107, 92, 112, 104, 88, 108, 100,  # 1930-1939
                  85, 104, 96, 116, 101, 92, 112, 97, 89, 108,  # 1940-1949
                  100, 85, 105, 96, 109, 101, 93, 112, 97, 89,  # 1950-1959
                  109, 93, 113, 105, 90, 109, 101, 86, 106, 97,  # 1960-1969
                  89, 102, 94, 113, 105, 90, 110, 101, 86, 106,  # 1970-1979
                  98, 110, 102, 94, 114, 98, 90, 110, 95, 86,  # 1980-1989
                  106, 91, 111, 102, 94, 107, 99, 90, 103, 95,  # 1990-1999
                  115, 106, 91, 111, 103, 87, 107, 99, 84, 103,  # 2000-2009
                  95, 115, 100, 91, 111, 96, 88, 107, 92, 112,  # 2010-2019
                  104, 95, 108, 100, 92, 111, 96, 88, 108, 92,  # 2020-2029
                  112, 104, 89, 108, 100, 85, 105, 96, 116, 101,  # 2030-2039
                  93, 112, 97, 89, 109, 100, 85, 105, 97, 109,  # 2040-2049
                  101, 93, 113, 97, 89, 109, 94, 113, 105, 90,  # 2050-2059
                  110, 101, 86, 106, 98, 89, 102, 94, 114, 105,  # 2060-2069
                  90, 110, 102, 86, 106, 98, 111, 102, 94, 114,  # 2070-2079
                  99, 90, 110, 95, 87, 106, 91, 111, 103, 94,  # 2080-2089
                  107, 99, 91, 103, 95, 115, 107, 91, 111, 103,  # 2090-2099
                  88, 108, 100, 85, 105, 96, 109, 101, 93, 112,  # 2100-2109
                  97, 89, 109, 93, 113, 105, 90, 109, 101, 86,  # 2110-2119
                  106, 97, 89, 102, 94, 113, 105, 90, 110, 101,  # 2120-2129
                  86, 106, 98, 110, 102, 94, 114, 98, 90, 110,  # 2130-2139
                  95, 86, 106, 91, 111, 102, 94, 107, 99, 90,  # 2140-2149
                  103, 95, 115, 106, 91, 111, 103, 87, 107, 99,  # 2150-2159
                  84, 103, 95, 115, 100, 91, 111, 96, 88, 107,  # 2160-2169
                  92, 112, 104, 95, 108, 100, 92, 111, 96, 88,  # 2170-2179
                  108, 92, 112, 104, 89, 108, 100, 85, 105, 96,  # 2180-2189
                  116, 101, 93, 112, 97, 89, 109, 100, 85, 105]  # 2190-2199
        return easter[y - 1901]

    ################ B3 ################
    def __is_business_day_b3(self, date: dt.date):
        em = self.__easter_monday(date.year)
        if (date.weekday() == SAT or date.weekday() == SUN
                or (date.day == 1 and date.month == 1)
                or (date.day == 25 and date.month == 1 and date.year <= 2021)
                or (date.day == 21 and date.month == 4)
                or (date.day == 1 and date.month == 5)
                or (date.day == 9 and date.month == 7 and date.year != 2020 and date.year <= 2021)
                or (date.day == 7 and date.month == 9)
                or (date.day == 12 and date.month == 10)
                or (date.day == 2 and date.month == 11)
                or (date.day == 15 and date.month == 11)
                or (date.day == 12 and date.month == 6 and date.year == 2014)  # copa do mundo
                or (date.day == 20 and date.month == 11 and date.year >= 2006 and date.year != 2020 and date.year <= 2021)
                or (date.day == 24 and date.month == 12)
                or (date.day == 25 and date.month == 12)
                or (date.timetuple().tm_yday == em - 3)
                or (date.timetuple().tm_yday == em - 49 or date.timetuple().tm_yday == em - 48)
                or (date.timetuple().tm_yday == em + 59)
                or (date.month == 12 and (date.day == 31 or (date.day >= 29 and date.weekday() == FRI)))):
            return False
        return True

    ################ BRAZIL ################
    def __is_business_day_brazil(self, date: dt.date):
        em = self.__easter_monday(date.year)
        if (date.weekday() == SAT or date.weekday() == SUN
                or (date.day == 1 and date.month == 1)
                or (date.day == 21 and date.month == 4)
                or (date.day == 1 and date.month == 5)
                or (date.day == 7 and date.month == 9)
                or (date.day == 12 and date.month == 10)
                or (date.day == 2 and date.month == 11)
                or (date.day == 15 and date.month == 11)
                or (date.day == 25 and date.month == 12)
                or (date.timetuple().tm_yday == em - 3)
                or (date.timetuple().tm_yday == em - 49 or date.timetuple().tm_yday == em - 48)
                or (date.timetuple().tm_yday == em + 59)):
            return False
        return True

    ################ US ################
    def __is_washington_birthday(self, d, m, y, w):
        if (y >= 1971):
            # third Monday in February
            return (d >= 15 and d <= 21) and w == MON and m == 2
        else:
            # February 22nd, possily adjusted
            return (d == 22 or (d == 23 and w == MON)
                    or (d == 21 and w == FRI)) and m == 2

    def __is_memorial_day(self, d, m, y, w):
        if (y >= 1971):
            # last Monday in May
            return d >= 25 and w == MON and m == 5
        else:
            # May 30th, possibly adjusted
            return (d == 30 or (d == 31 and w == MON)
                    or (d == 29 and w == FRI)) and m == 5

    def __is_veterans_day(self, d, m, y, w):
        if (y <= 1970 or y >= 1978):
            # November 11th, adjusted
            return (d == 11 or (d == 12 and w == MON) or
                    (d == 10 and w == FRI)) and m == 11
        else:
            # fourth Monday in October
            return (d >= 22 and d <= 28) and w == MON and m == 10

    def __is_business_day_us_settle(self, date: dt.date):
        w = date.weekday()
        d = date.day
        m = date.month
        y = date.year
        if ((w == SAT or w == SUN)
                # New Year's Day (possibly moved to Monday if on Sunday)
                or ((d == 1 or (d == 2 and w == MON)) and m == 1)
                # (or to Friday if on Saturday)
                or (d == 31 and w == FRI and m == 12)
                # Martin Luther King's birthday (third Monday in January)
                or ((d >= 15 and d <= 21) and w == MON and m == 1 and y >= 1983)
                # Washington's birthday (third Monday in February)
                or self.__is_washington_birthday(d, m, y, w)
                # Memorial Day (last Monday in May)
                or self.__is_memorial_day(d, m, y, w)
                # Independence Day (Monday if Sunday or Friday if Saturday)
                or ((d == 4 or (d == 5 and w == MON) or
                     (d == 3 and w == FRI)) and m == 7)
                # Labor Day (first Monday in September)
                or (d <= 7 and w == MON and m == 9)
                # Columbus Day (second Monday in October)
                or ((d >= 8 and d <= 14) and w == MON and m == 10 and y >= 1971)
                # Veteran's Day (Monday if Sunday or Friday if Saturday)
                or self.__is_veterans_day(d, m, y, w)
                # Thanksgiving Day (fourth Thursday in November)
                or ((d >= 22 and d <= 28) and w == THU and m == 11)
                # Christmas (Monday if Sunday or Friday if Saturday)
                or ((d == 25 or (d == 26 and w == MON) or
                     (d == 24 and w == FRI)) and m == 12)):
            return False
        return True

    def workday(self, date: dt.datetime, bd: int) -> dt.datetime:
        if bd < 0:
            step = -1
        else:
            step = 1
        while bd != 0:
            date += timedelta(days=step)
            if self.calendarType == CalendarType.BR:
                if self.__is_business_day_brazil(date):
                    bd -= step
            elif self.calendarType == CalendarType.B3:
                if self.__is_business_day_b3(date):
                    bd -= step
            elif self.calendarType == CalendarType.US:
                if self.__is_business_day_us_settle(date):
                    bd -= step
            elif self.calendarType == CalendarType.NOCAL:
                if date.weekday() != SAT and date.weekday() != SUN:
                    bd -= step
            else:
                raise Exception('Calendar not valid')
        return date

    def networkdays(self, begin: dt.datetime, end: dt.datetime) -> int:
        num_days = 0
        m = 1
        if begin > end:
            aux = begin
            begin = end
            end = aux
            m = -1
        while begin != end:
            begin = begin + timedelta(days=1)
            if self.calendarType == CalendarType.BR:
                if self.__is_business_day_brazil(begin):
                    num_days += 1
            elif self.calendarType == CalendarType.B3:
                if self.__is_business_day_b3(begin):
                    num_days += 1
            elif self.calendarType == CalendarType.US:
                if self.__is_business_day_us_settle(begin):
                    num_days += 1
            elif self.calendarType == CalendarType.NOCAL:
                if begin.weekday() != SAT and begin.weekday() != SUN:
                    num_days += 1
            else:
                raise Exception('Calendar not valid')

        return m * num_days

    def is_business_day(self, date: dt.datetime) -> bool:
        if self.calendarType == CalendarType.B3:
            return self.__is_business_day_b3(date)
        elif self.calendarType == CalendarType.BR:
            return self.__is_business_day_brazil(date)
        elif self.calendarType == CalendarType.US:
            return self.__is_business_day_us_settle(date)
        elif self.calendarType == CalendarType.NOCAL:
            if date.weekday() != SAT and date.weekday() != SUN:
                return True
            else:
                return False
        else:
            raise ('Unknown calendar')
