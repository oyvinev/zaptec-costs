from datetime import datetime
import requests

from zaptec_costs.src.secrets import Secrets


class StrompriserApi(requests.Session):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.strompriser.no/public/"
        self.headers.update({"api-key": Secrets.strompriser_api_key})

    def get_prices(self, start_date, end_date):
        response = self.get(
            self.base_url + "prices",
            params={"startDate": start_date, "endDate": end_date, "region": 1},
        )
        price_per_hour = dict()
        for day in response.json():
            date = datetime.strptime(day["date"], "%Y-%m-%dT%H:%M:%S.%f%z")
            date = datetime.utcfromtimestamp(date.timestamp())
            for hour, price in enumerate(day["dailyPriceArray"]):
                price_per_hour[date.replace(hour=hour)] = price / 100.0 * 1.25
        return price_per_hour
