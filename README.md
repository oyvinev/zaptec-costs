# Calculate costs of Zaptec chargers

Simple program to calculate monthly costs of all Zaptec chargers associated with your Zaptec account

It is based on Elvia tariffs and electricity prices in NO1

## Requirements

- Zaptec username/password
- [Elvia API key](https://assets.ctfassets.net/jbub5thfds15/3Jm2yspPw1kFmDEkzdjhfw/e3a153543d8f95e889285248e5af21af/Elvia_GridTariffAPI_for_smart_house_purposes_DIGIN.pdf)
- [Strømpriser.no API key](https://www.strompriser.no/artikler/api-for-strompriser)
- Python 3.10+

No third party dependencies

## Usage

Run `python main.py`

This will print a summary of all charger costs per month, calculated from hourly prices.

## Environment variables

The following environment variables will be used if present, instead of requesting for username/passwords/api on stdin:

- `ZAPTEC_USERNAME`
- `ZAPTEC_PASSWORD`
- `STROMPRISER_API_KEY`
- `ELVIA_API_KEY`