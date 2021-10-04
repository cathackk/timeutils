from datetime import date
from datetime import timedelta
from enum import IntEnum
from typing import Iterable


class Weekday(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def __add__(self, other: int) -> 'Weekday':
        """
            >>> Weekday.MONDAY + 1
            Weekday.TUESDAY
            >>> Weekday.MONDAY + 5
            Weekday.SATURDAY
            >>> Weekday.SUNDAY + 1
            Weekday.MONDAY
            >>> Weekday.SUNDAY + 3
            Weekday.WEDNESDAY
        """
        return type(self)((self.value + other - 1) % 7 + 1)

    def __sub__(self, other):
        """
            >>> Weekday.SUNDAY - 1
            Weekday.SATURDAY
            >>> Weekday.MONDAY - 3
            Weekday.FRIDAY
            >>> Weekday.THURSDAY - Weekday.TUESDAY
            2
            >>> Weekday.TUESDAY - Weekday.THURSDAY
            5
        """
        if isinstance(other, type(self)):
            return (int(self) - int(other)) % 7
        else:
            return self + (-other)

    @classmethod
    def for_date(cls, date_: date):
        return cls(date_.isoweekday())

    def first_of_year(self, year: int) -> date:
        """
            >>> Weekday.MONDAY.first_of_year(2001)
            datetime.date(2001, 1, 1)
            >>> Weekday.TUESDAY.first_of_year(2001)
            datetime.date(2001, 1, 2)
            >>> Weekday.THURSDAY.first_of_year(2001)
            datetime.date(2001, 1, 4)
            >>> Weekday.THURSDAY.first_of_year(2002)
            datetime.date(2002, 1, 3)
            >>> Weekday.THURSDAY.first_of_year(2003)
            datetime.date(2003, 1, 2)
            >>> Weekday.THURSDAY.first_of_year(2004)
            datetime.date(2004, 1, 1)
            >>> Weekday.THURSDAY.first_of_year(2005)
            datetime.date(2005, 1, 6)
            >>> Weekday.THURSDAY.first_of_year(2006)
            datetime.date(2006, 1, 5)
            >>> Weekday.THURSDAY.first_of_year(2010)
            datetime.date(2010, 1, 7)
        """
        day = 1 + (self.value - date(year, 1, 1).isoweekday()) % 7
        return date(year, 1, day)


SEVEN_DAYS = timedelta(days=7)


class Week:
    """
        >>> w = Week(date(2021, 1, 18))
        >>> w
        Week(datetime.date(2021, 1, 18))
        >>> print(w)
        2021-W03
        >>> w.start
        datetime.date(2021, 1, 18)
        >>> w.end
        datetime.date(2021, 1, 25)
        >>> w.first_weekday
        Weekday.MONDAY
        >>> w.year
        2021
        >>> w.number
        3
        >>> len(w)
        7
        >>> date(2021, 1, 18) in w
        True
        >>> date(2021, 1, 25) in w
        False
    """

    __slots__ = ('start',)

    def __init__(self, start: date):
        self.start = start

    @classmethod
    def with_date(cls, date_: date, first_weekday: Weekday = Weekday.MONDAY) -> 'Week':
        """
            >>> Week.with_date(date(2020, 12, 28))
            Week(datetime.date(2020, 12, 28))
            >>> Week.with_date(date(2020, 12, 31))
            Week(datetime.date(2020, 12, 28))
            >>> Week.with_date(date(2021, 1, 1))
            Week(datetime.date(2020, 12, 28))
            >>> Week.with_date(date(2021, 1, 3))
            Week(datetime.date(2020, 12, 28))
            >>> Week.with_date(date(2021, 1, 4))
            Week(datetime.date(2021, 1, 4))
            >>> Week.with_date(date(2021, 1, 2), first_weekday=Weekday.SUNDAY)
            Week(datetime.date(2020, 12, 27))
            >>> Week.with_date(date(2021, 1, 3), first_weekday=Weekday.SUNDAY)
            Week(datetime.date(2021, 1, 3))
            >>> Week.with_date(date(2021, 1, 4), first_weekday=Weekday.SUNDAY)
            Week(datetime.date(2021, 1, 3))
        """
        return cls(date_ - timedelta(days=(date_.isoweekday() - int(first_weekday)) % 7))

    @classmethod
    def with_number(cls, year: int, number: int, first_weekday: Weekday = Weekday.MONDAY) -> 'Week':
        """
            >>> Week.with_number(2021, 0)
            Week(datetime.date(2020, 12, 28))
            >>> Week.with_number(2021, 1)
            Week(datetime.date(2021, 1, 4))
            >>> Week.with_number(2021, 2)
            Week(datetime.date(2021, 1, 11))
            >>> Week.with_number(2021, 30).number
            30

            >>> Week.with_number(2021, 0, first_weekday=Weekday.SUNDAY)
            Week(datetime.date(2020, 12, 27))
            >>> Week.with_number(2021, 1, first_weekday=Weekday.SUNDAY)
            Week(datetime.date(2021, 1, 3))
            >>> Week.with_number(2021, 2, first_weekday=Weekday.SUNDAY)
            Week(datetime.date(2021, 1, 10))
            >>> Week.with_number(2021, 33, first_weekday=Weekday.SUNDAY).number
            33
        """
        # TODO: handle number out of range? (0? 53?)
        first_midday = (first_weekday + 3).first_of_year(year)
        return cls(first_midday + timedelta(days=7 * (number - 1) - 3))

    @classmethod
    def now(cls, first_weekday: Weekday = Weekday.MONDAY) -> 'Week':
        return cls.with_date(date.today(), first_weekday)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.start!r})'

    def __str__(self) -> str:
        return f'{self.year}-W{self.number:02}'

    @property
    def end(self) -> date:
        return self.start + SEVEN_DAYS

    def __len__(self) -> int:
        return len(Weekday)  # 7 :)

    def __contains__(self, date_: date) -> bool:
        """
            >>> w = Week(date(2021, 9, 27))
            >>> w.start, w.end
            (datetime.date(2021, 9, 27), datetime.date(2021, 10, 4))
            >>> date(2021, 9, 1) in w
            False
            >>> date(2021, 9, 26) in w
            False
            >>> date(2021, 9, 27) in w
            True
            >>> date(2021, 9, 30) in w
            True
            >>> date(2021, 10, 1) in w
            True
            >>> date(2021, 10, 3) in w
            True
            >>> date(2021, 10, 4) in w
            False
            >>> date(2021, 11, 1) in w
            False
        """
        return self.start <= date_ < self.end

    def __iter__(self):
        """
            >>> w = Week.with_number(2021, 30)
            >>> (w.start, w.end)
            (datetime.date(2021, 7, 26), datetime.date(2021, 8, 2))
            >>> ', '.join(str(d) for d in Week.with_number(2021, 30))
            '2021-07-26, 2021-07-27, 2021-07-28, 2021-07-29, 2021-07-30, 2021-07-31, 2021-08-01'
        """
        for offset in range(len(self)):
            yield self.start + timedelta(days=offset)

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self.start == other.start

    def __hash__(self) -> int:
        return hash((type(self), self.start))

    def __gt__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise NotImplementedError
        return self.start > other.start

    def __add__(self, other) -> 'Week':
        """
            >>> w = Week(date(2021, 9, 27))
            >>> w + 1
            Week(datetime.date(2021, 10, 4))
            >>> w + 2
            Week(datetime.date(2021, 10, 11))
            >>> w + timedelta(days=21)
            Week(datetime.date(2021, 10, 18))
            >>> w + timedelta(days=1)
            Traceback (most recent call last):
            ...
            ValueError: must add only whole weeks
        """
        if not hasattr(other, 'days'):
            other = timedelta(days=7 * other)

        if other.days % 7 != 0:
            raise ValueError('must add only whole weeks')

        return type(self)(self.start + other)

    def __sub__(self, other) -> 'Week':
        """
            >>> Week(date(2021, 9, 27)) - 1
            Week(datetime.date(2021, 9, 20))
            >>> Week(date(2021, 9, 27)) - 2
            Week(datetime.date(2021, 9, 13))
            >>> Week(date(2021, 9, 27)) - timedelta(days=21)
            Week(datetime.date(2021, 9, 6))
        """
        return self + (-other)

    @property
    def first_weekday(self) -> Weekday:
        return Weekday.for_date(self.start)

    def weekday_date(self, weekday: Weekday) -> date:
        """
            >>> w = Week(date(2021, 9, 27))
            >>> w.first_weekday
            Weekday.MONDAY
            >>> w.weekday_date(Weekday.MONDAY)
            datetime.date(2021, 9, 27)
            >>> w.weekday_date(Weekday.TUESDAY)
            datetime.date(2021, 9, 28)
            >>> w.weekday_date(Weekday.THURSDAY)
            datetime.date(2021, 9, 30)
            >>> w.weekday_date(Weekday.FRIDAY)
            datetime.date(2021, 10, 1)
            >>> w.weekday_date(Weekday.SUNDAY)
            datetime.date(2021, 10, 3)
            >>> w2 = Week(date(2021, 9, 26))
            >>> w2.first_weekday
            Weekday.SUNDAY
            >>> w2.weekday_date(Weekday.SUNDAY)
            datetime.date(2021, 9, 26)
            >>> w2.weekday_date(Weekday.MONDAY)
            datetime.date(2021, 9, 27)
            >>> w2.weekday_date(Weekday.SATURDAY)
            datetime.date(2021, 10, 2)
        """
        return self.start + timedelta(days=weekday - self.first_weekday)

    @property
    def year(self) -> int:
        """
            >>> Week(date(2021, 10, 27)).year
            2021
            >>> Week(date(2001, 12, 31)).year
            2002
            >>> Week(date(2024, 12, 30)).year
            2025
        """
        return (self.start + timedelta(days=3)).year

    @property
    def number(self) -> int:
        """
            >>> Week(date(2021, 10, 4)).number
            40
            >>> Week(date(2021, 1, 3)).number  # SUN 2021-01-03
            1
            >>> Week(date(2021, 1, 4)).number  # MON 2021-01-04
            1
            >>> Week(date(2021, 12, 26)).number  # SUN 2021-12-26
            52
            >>> Week(date(2021, 12, 27)).number  # MON 2021-12-27
            52
            >>> Week(date(2020, 12, 28)).number
            53
        """
        my_midday = self.start + timedelta(days=3)
        first_midday = (self.first_weekday + 3).first_of_year(self.year)
        return 1 + (my_midday - first_midday).days // 7


def weeks_of_year(year: int, first_weekday: Weekday = Weekday.MONDAY) -> Iterable[Week]:
    """
        >>> weeks_2021 = list(weeks_of_year(2021))
        >>> len(weeks_2021)
        52
        >>> weeks_2021[0], weeks_2021[-1]
        (Week(datetime.date(2021, 1, 4)), Week(datetime.date(2021, 12, 27)))
        >>> print(weeks_2021[0], weeks_2021[-1])
        2021-W01 2021-W52

        >>> weeks_2020 = list(weeks_of_year(2020))
        >>> len(weeks_2020)
        53
        >>> weeks_2020[0], weeks_2020[-1]
        (Week(datetime.date(2019, 12, 30)), Week(datetime.date(2020, 12, 28)))
        >>> print(weeks_2020[0], weeks_2020[-1])
        2020-W01 2020-W53
    """
    w = Week.with_number(year, 1, first_weekday)
    while w.year <= year:
        yield w
        w += SEVEN_DAYS


class WeekRange:
    pass
