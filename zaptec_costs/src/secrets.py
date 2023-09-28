import os
from getpass import getpass


class _Secrets:
    zaptec_username: str
    zaptec_password: str
    elvia_api_key: str
    strompriser_api_key: str

    def __init__(self):
        if "ZAPTEC_USERNAME" in os.environ:
            self.zaptec_username = os.environ["ZAPTEC_USERNAME"]
        else:
            self.zaptec_username = input("Zaptec username: ")

        if "ZAPTEC_PASSWORD" in os.environ:
            self.zaptec_password = os.environ["ZAPTEC_PASSWORD"]
        else:
            self.zaptec_password = getpass("Zaptec password: ")

        if "ELVIA_API_KEY" in os.environ:
            self.elvia_api_key = os.environ["ELVIA_API_KEY"]
        else:
            self.elvia_api_key = getpass("Elvia API key: ")

        if "STROMPRISER_API_KEY" in os.environ:
            self.strompriser_api_key = os.environ["STROMPRISER_API_KEY"]
        else:
            self.strompriser_api_key = getpass("Strompriser API key: ")


Secrets = _Secrets()
