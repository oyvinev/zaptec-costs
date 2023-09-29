from collections import defaultdict
from functools import lru_cache
import requests
from datetime import datetime
from zaptec_costs.src.models import ChargingSession

from zaptec_costs.src.secrets import Secrets
from zaptec_costs.src.utils import utc_to_local


class ZaptecApi(requests.Session):
    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.authenticate()
        self.base_url = "https://api.zaptec.com/api/"
        self.url = lambda x: self.base_url + x

    def authenticate(self):
        response = self.post(
            "https://api.zaptec.com/oauth/token",
            data={
                "grant_type": "password",
                "username": Secrets.zaptec_username,
                "password": Secrets.zaptec_password,
            },
        )
        self.headers.update({"Authorization": "Bearer " + response.json()["access_token"]})

    @staticmethod
    def floor(timestamp):
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
        return datetime.fromtimestamp(dt.replace(minute=0, second=0, microsecond=0).timestamp())

    @lru_cache(maxsize=1)
    def get_chargers(self):
        response = self.get(self.base_url + "chargers")
        assert (
            response.status_code == 200
        ), f"Failed to get chargers: {response.status_code} ({response.text})"
        assert response.json()["Pages"] <= 1, "More than one page of chargers"
        return response.json()["Data"]

    @lru_cache(maxsize=128)
    def get_charging_sessions(self, charger_id):
        response = self.get(
            self.base_url + "chargehistory/",
            params={
                "chargerId": charger_id,
                "detailLevel": 1,
                "pageIndex": 0,
                "pageSize": 5000,
                "sortDescending": "true",
            },
        )
        assert (
            response.json()["Pages"] <= 1
        ), "More than one page of charge history - not implemented"

        for charge_session in response.json()["Data"]:
            yield ChargingSession(
                charger_name=charge_session["DeviceName"],
                start_time=utc_to_local(
                    datetime.strptime(charge_session["StartDateTime"], "%Y-%m-%dT%H:%M:%S.%f")
                ),
                end_time=utc_to_local(
                    datetime.strptime(charge_session["EndDateTime"], "%Y-%m-%dT%H:%M:%S.%f")
                ),
                energy_usage=[
                    (
                        utc_to_local(datetime.strptime(x["Timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")),
                        x["Energy"],
                    )
                    for x in charge_session["EnergyDetails"]
                ],
            )
