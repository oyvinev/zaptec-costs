from dataclasses import dataclass
from pydantic import BaseModel, Field, model_validator, computed_field
from datetime import datetime, timedelta

import requests

from zaptec_costs.src.secrets import Secrets


class ChargingSession(BaseModel):
    charger_name: str
    start_time: datetime
    end_time: datetime
    energy_usage: list[tuple[datetime, float]] = Field(repr=False)

    @computed_field
    def duration(self) -> timedelta:
        return self.end_time - self.start_time

    @computed_field
    @property
    def kwh(self) -> float:
        return sum(energy for _, energy in self.energy_usage)

    @computed_field
    @property
    def kwh_per_hour(self) -> float:
        return self.kwh / self.duration.total_seconds() * 3600

    @computed_field
    @property
    def tariff(self) -> float:
        s = 0.0
        for ts, energy in self.energy_usage:
            tariff = Tariff()(ts, energy)
            s += tariff
        return s

    @computed_field
    @property
    def energy_cost(self) -> float:
        s = 0.0
        for ts, energy in self.energy_usage:
            energy_cost = EnergyPrices()(ts, energy)
            s += energy_cost
        return s

    @computed_field
    @property
    def cost(self) -> float:
        return self.tariff + self.energy_cost

    @computed_field
    @property
    def cost_inc_vat(self) -> float:
        return self.cost * 1.25


class ChargingTotals(BaseModel):
    charging_sessions: list[ChargingSession]

    @model_validator(mode="after")
    def check(cls, values):
        # Sort sessions by start time
        values.charging_sessions = sorted(values.charging_sessions, key=lambda x: x.start_time)
        return values

    @computed_field
    @property
    def num_sessions(self) -> int:
        return len(self.charging_sessions)

    @computed_field
    @property
    def kwh(self) -> float:
        return sum(cs.kwh for cs in self.charging_sessions)

    @computed_field
    @property
    def cost(self) -> float:
        return sum(cs.cost for cs in self.charging_sessions)

    @computed_field
    @property
    def cost_inc_vat(self) -> float:
        return sum(cs.cost_inc_vat for cs in self.charging_sessions)


class EnergyPrices(requests.Session):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def prices(self):
        if not hasattr(self, "_prices"):
            print("getting energy prices")
            price_per_hour = dict()
            for day in DATE_RANGE().iter(days=1):
                url = "https://www.hvakosterstrommen.no/api/v1/prices/" + datetime.strftime(
                    day, "%Y/%m-%d_NO1.json"
                )
                response = self.get(url)
                for hourly_price in response.json():
                    price_per_hour[
                        datetime.strptime(hourly_price["time_start"], "%Y-%m-%dT%H:%M:%S%z")
                    ] = hourly_price["NOK_per_kWh"]
            self._prices = price_per_hour
        return self._prices

    def __call__(self, timestamp: datetime, kwh: float):
        ts = timestamp.replace(minute=0, second=0, microsecond=0)
        return self.prices[ts] * kwh


class Tariff(requests.Session):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.headers.update({"X-API-Key": Secrets.elvia_api_key})
        self.base_url = "https://elvia.azure-api.net/grid-tariff/digin/api/1.0/"

    @property
    def tariffs(self):
        if not hasattr(self, "_tariffs"):
            start_date = DATE_RANGE().str().start
            end_date = DATE_RANGE().str().end
            response = self.get(
                self.base_url + "tariffquery",
                params={
                    "TariffKey": "standard",
                    "StartTime": start_date,
                    "EndTime": end_date,
                },
            )
            tariffs = dict()
            for tariff_price in response.json()["gridTariff"]["tariffPrice"]["hours"]:
                tariffs[
                    datetime.strptime(tariff_price["startTime"], "%Y-%m-%dT%H:%M:%S%z")
                ] = tariff_price["energyPrice"]["total"]
            self._tariffs = tariffs
        return self._tariffs

    def __call__(self, timestamp: datetime, kwh: float):
        ts = timestamp.replace(minute=0, second=0, microsecond=0)
        return self.tariffs[ts] * kwh


@dataclass
class DATE_RANGE_STR:
    start: str
    end: str


class DATE_RANGE(BaseModel):
    start: datetime = datetime.now().replace(
        month=datetime.now().month - 1, day=1, hour=0, minute=0, second=0, microsecond=0
    )
    end: datetime = datetime.now().replace(
        month=datetime.now().month, hour=0, minute=0, second=0, microsecond=0
    )

    padding: timedelta | None = timedelta(days=1)

    @model_validator(mode="after")
    def check(cls, values):
        if values.padding:
            values.start = values.start - values.padding
            values.end = values.end + values.padding
        return values

    def str(self, format="%Y-%m-%d"):
        return DATE_RANGE_STR(
            datetime.strftime(self.start, format), datetime.strftime(self.end, format)
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
