from src.secrets import Secrets
from src.date import DATE_RANGE
from src.elvia_api import ElviaApi
from src.strompriser_api import StrompriserApi
from src.zaptec_api import ZaptecApi


if __name__ == "__main__":
    tariffs = ElviaApi().get_tariffs(DATE_RANGE.str().start, DATE_RANGE.str().end)
    power_prices = StrompriserApi().get_prices(DATE_RANGE.str().start, DATE_RANGE.str().end)
    zaptec_api = ZaptecApi()

    power_costs = dict()
    tariff_costs = dict()
    usage = dict()

    for charger in zaptec_api.get_chargers():
        power_costs[charger["Name"]] = dict()
        tariff_costs[charger["Name"]] = dict()
        usage[charger["Name"]] = dict()
        for month in DATE_RANGE().iter(months=1):
            power_costs[charger["Name"]][month] = 0
            tariff_costs[charger["Name"]][month] = 0
            usage[charger["Name"]][month] = 0

        energy_usage = zaptec_api.get_energy_usage(charger["Id"])
        for hour in DATE_RANGE().iter(hours=1):
            kwh = energy_usage.get(hour, 0)
            power_cost = power_prices[hour] * kwh
            tariff_cost = tariffs[hour] * kwh

            month = hour.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            power_costs[charger["Name"]][month] += power_cost
            tariff_costs[charger["Name"]][month] += tariff_cost
            usage[charger["Name"]][month] += kwh

    for month in DATE_RANGE().iter(months=1):
        print(month.strftime("%B %Y"))
        for charger in zaptec_api.get_chargers():
            costs = power_costs[charger["Name"]][month] + tariff_costs[charger["Name"]][month]
            cost_per_kwh = costs / (usage[charger["Name"]][month] + 1e-16)
            tariff_per_kwh = tariff_costs[charger["Name"]][month] / (
                usage[charger["Name"]][month] + 1e-16
            )
            energy_price_per_kwh = power_costs[charger["Name"]][month] / (
                usage[charger["Name"]][month] + 1e-16
            )
            print(
                f"{charger['Name']}: {costs:.2f} kr ({usage[charger['Name']][month]:.2f} kWh, {cost_per_kwh:.2f} kr/kWh)",
                end=" - ",
            )
            print(
                f"Nettleie: {tariff_costs[charger['Name']][month]:.2f} kr ({tariff_per_kwh:.2f} kr/kWh)",
                end=" - ",
            )
            print(
                f"Strøm: {power_costs[charger['Name']][month]:.2f} kr ({energy_price_per_kwh:.2f} kr/kWh)"
            )

        print()
