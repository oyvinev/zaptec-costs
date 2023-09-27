from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class DATE_RANGE_STR:
    start: str
    end: str


@dataclass
class DATE_RANGE:
    start: datetime = datetime.now().replace(
        month=datetime.now().month - 4, day=1, hour=0, minute=0, second=0, microsecond=0
    )
    end: datetime = datetime.now().replace(
        month=datetime.now().month, hour=0, minute=0, second=0, microsecond=0
    )

    @classmethod
    def str(cls, format="%Y-%m-%d"):
        return DATE_RANGE_STR(
            datetime.strftime(cls.start, format), datetime.strftime(cls.end, format)
        )

    def _iter_months(self, months):
        start = self.start
        while start <= self.end:
            yield start
            start = start.replace(
                month=start.month + months,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

    def iter(self, **kwargs):
        if "months" in kwargs:
            assert len(kwargs) == 1, "Months can not be specified with other arguments"
            yield from self._iter_months(kwargs["months"])
        else:
            increment = timedelta(**kwargs)
            start = self.start
            while start + increment <= self.end:
                yield start
                start += increment
