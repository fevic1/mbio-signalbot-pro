import argparse

from aios.system import AIOSBootstrap
from aios.system.runtime import AIOSRuntime

from aios.cli.commands.inspect import inspect
from aios.cli.commands.health import health
from aios.cli.commands.memory import memory
from aios.cli.commands.events import events
from aios.cli.commands.status import status
from aios.cli.commands.stop import stop as stop_command


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

        print(
            stop_command()
        )


    elif args.command == "status":

        print(
            status()
        )


    elif args.command in [
        "inspect",
        "health",
        "memory",
        "events",
    ]:

        container = AIOSBootstrap().initialize()


        if args.command == "inspect":

            print(
                inspect(container)
            )

        elif args.command == "health":

            print(
                health(container)
            )

        elif args.command == "memory":

            print(
                memory(container)
            )

        elif args.command == "events":

            print(
                events(container)
            )


    else:

        raise SystemExit(
            "Unknown command"
        )


if __name__ == "__main__":

    main()
