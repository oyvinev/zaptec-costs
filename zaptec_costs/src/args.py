import argparse
from datetime import datetime, timedelta


def parse_args():
    def valid_month(month):
        try:
            return datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise argparse.ArgumentTypeError(f"{month} is not a valid month")

    parser = argparse.ArgumentParser()
    now = datetime.now()
    group = parser.add_mutually_exclusive_group()
    argument_group = group.add_argument_group()

    argument_group.add_argument(
        "--start",
        type=valid_month,
        # default=now.replace(month=now.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0),
        required=False,
    )
    argument_group.add_argument(
        "--end",
        type=valid_month,
        # default=now.replace(month=now.month, day=1, hour=0, minute=0, second=0, microsecond=0)
        # - timedelta(seconds=1),
        required=False,
    )

    group.add_argument("--month", type=valid_month, required=False)

    args = parser.parse_args()
    if args.month and (args.start or args.end):
        parser.error("Month can not be specified with start or end")
    if args.start and args.end and args.start > args.end:
        parser.error("Start must be before end")
    if args.start and not args.end:
        parser.error("Start must be specified with end")
    if args.end and not args.start:
        parser.error("End must be specified with start")

    if args.month:
        args.start = args.month
        args.end = args.month.replace(
            year=args.month.year + (args.month.month + 1) // 12,
            month=(args.month.month + 1) % 12,
        ) - timedelta(seconds=1)
    elif not args.start and not args.end:
        args.start = now.replace(
            month=now.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        args.end = now.replace(
            month=now.month, day=1, hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(seconds=1)
    if args.end > now:
        args.end = now
    del args.month  # type: ignore
    return args


Args = parse_args()
