import requests
import datetime

from src.secrets import Secrets


class ElviaApi(requests.Session):
    def __init__(self):
        super().__init__()
        self.headers.update({"X-API-Key": Secrets.elvia_api_key})
        self.base_url = "https://elvia.azure-api.net/grid-tariff/digin/api/1.0/"

    @staticmethod
    def floor(timestamp: str):
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
        dt = datetime.datetime.utcfromtimestamp(dt.timestamp())
        return datetime.datetime.fromtimestamp(
            dt.replace(minute=0, second=0, microsecond=0).timestamp()
        )

    def get_tariffs(self, start_date, end_date):
        response = self.get(
            self.base_url + "tariffquery",
            params={
                "TariffKey": "standard",
                "StartTime": start_date,
                "EndTime": end_date,
            },
        )
        tariff = dict()
        for tariff_price in response.json()["gridTariff"]["tariffPrice"]["hours"]:
            tariff[self.floor(tariff_price["startTime"])] = tariff_price["energyPrice"]["total"]
        return tariff
