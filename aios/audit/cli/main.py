import argparse

from aios.audit.commands.architecture import run


def main():

    parser = argparse.ArgumentParser(
        prog="aios-audit"
    )

    sub = parser.add_subparsers(
        dest="command"
    )

    architecture = sub.add_parser(
        "architecture"
    )

    architecture.add_argument(
        "--strict",
        action="store_true",
    )

    args = parser.parse_args()


    if args.command == "architecture":

        run(
            strict=args.strict
        )


if __name__ == "__main__":
    main()
