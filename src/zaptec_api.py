from collections import defaultdict
import requests
import datetime

from src.secrets import Secrets


class ZaptecApi(requests.Session):
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
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
        return datetime.datetime.fromtimestamp(
            dt.replace(minute=0, second=0, microsecond=0).timestamp()
        )

    def get_chargers(self):
        response = self.get(self.base_url + "chargers")
        assert (
            response.status_code == 200
        ), f"Failed to get chargers: {response.status_code} ({response.text})"
        assert response.json()["Pages"] == 1, "More than one page of chargers"
        return response.json()["Data"]

    def get_energy_usage(self, charger_id):
        kwh = defaultdict(float)
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
            for energy_detail in charge_session["EnergyDetails"]:
                kwh[self.floor(energy_detail["Timestamp"])] += energy_detail["Energy"]
        return kwh
