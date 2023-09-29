from datetime import timedelta
import locale

from pathlib import Path
from jinja2 import Environment, PackageLoader

from zaptec_costs.src.models import DATE_RANGE, ChargingSession, ChargingTotals
from zaptec_costs.src.utils import get_valid_filename
from zaptec_costs.src.zaptec_api import ZaptecApi

locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")


def main():
    from zaptec_costs.src.models import Tariff
    from zaptec_costs.src.utils import utc_to_local
    from datetime import datetime

    env = Environment(loader=PackageLoader("zaptec_costs", str(Path(__file__).parent)))
    template = env.get_template("template.html")

    charging_sessions = split_charging_sessions_by_month(get_charging_session())
    charger_names = set(x.charger_name for x in charging_sessions)

    for name in charger_names:
        for month in DATE_RANGE(padding=None).iter(months=1):
            charging_totals = ChargingTotals(
                charging_sessions=[
                    x
                    for x in charging_sessions
                    if x.charger_name == name
                    and x.start_time.month == month.month
                    and x.start_time.year == month.year
                ]
            )

            # Render template.html using jinja
            # Write to filename
            filename = Path(get_valid_filename(f"{name}-{month.strftime('%B %Y')}.html"))
            with open(filename, "wt") as f:
                f.write(
                    template.render(
                        charger_name=name,
                        charging_totals=charging_totals,
                        month=month.strftime("%B %Y"),
                    )
                )


def get_charging_session() -> list[ChargingSession]:
    zaptec_api = ZaptecApi()
    return sum(
        (
            list(zaptec_api.get_charging_sessions(charger["Id"]))
            for charger in zaptec_api.get_chargers()
        ),
        [],
    )


def split_charging_sessions_by_month(
    charging_sessions: list[ChargingSession],
) -> list[ChargingSession]:
    """Split charging sessions going from one month to another into two separate charging sessions"""
    split_charging_sessions = []
    for charging_session in charging_sessions:
        if charging_session.start_time.month == charging_session.end_time.month:
            split_charging_sessions.append(charging_session)
        else:
            session1 = ChargingSession(
                charger_name=charging_session.charger_name,
                start_time=charging_session.start_time,
                end_time=charging_session.start_time.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                - timedelta(seconds=1),
                energy_usage=[
                    (ts, energy)
                    for ts, energy in charging_session.energy_usage
                    if ts.month == charging_session.start_time.month
                ],
            )
            session2 = ChargingSession(
                charger_name=charging_session.charger_name,
                start_time=charging_session.start_time.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                ),
                end_time=charging_session.end_time,
                energy_usage=[
                    (ts, energy)
                    for ts, energy in charging_session.energy_usage
                    if ts.month == charging_session.end_time.month
                ],
            )
            split_charging_sessions.extend([session1, session2])

    return split_charging_sessions


if __name__ == "__main__":
    main()
