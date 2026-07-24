import argparse

from aios.system import AIOSBootstrap
from aios.system.runtime import AIOSRuntime


def start():

    bootstrap = AIOSBootstrap()

    container = bootstrap.initialize()

    runtime = AIOSRuntime(
        container
    )

    state = runtime.start()

    print(
        {
            "status":
            "AIOS started",

            "state":
            state.describe(),
        }
    )



def stop():

    print(
        {
            "status":
            "AIOS shutdown requested"
        }
    )



def main():

    parser = argparse.ArgumentParser(
        prog="aios"
    )


    parser.add_argument(
        "command"
    )


    args = parser.parse_args()


    if args.command == "start":

        start()

    elif args.command == "stop":

        stop()

    else:

        raise SystemExit(
            "Unknown command"
        )


if __name__ == "__main__":

    main()
