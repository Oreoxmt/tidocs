import asyncio
from pathlib import Path

import click
import marimo
import rich
from hypercorn.asyncio import serve
from hypercorn.config import Config

from tidocs.pandoc_wrapper import Pandoc
from tidocs.__version__ import __version__

APPS = {"merge": "Merge Release Notes"}


def launch_marimo_app(appname: str, host: str, port: int) -> None:
    """Launch a marimo web application with the specified configuration.

    Args:
        appname: Name of the application to launch (must be a key in APPS)
        host: Host address to bind to
        port: Port number to listen on
    """
    base_path = Path(__file__).parent
    script_path = base_path / appname / "main_marimo.py"

    app = marimo.create_asgi_app().with_app(path="", root=str(script_path)).build()
    config = Config()
    config.loglevel = "WARNING"
    config.bind = [f"{host}:{port}"]

    rich.print(f":sparkles: Running marimo app [bold magenta]{APPS[appname]}")
    rich.print(f":link: URL: http://{host}:{port}")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        serve(app, config, shutdown_trigger=lambda: asyncio.Future())
    )


@click.command(no_args_is_help=True)
@click.version_option(version=__version__)
@click.argument("appname", type=click.Choice(list(APPS.keys())), required=True)
@click.option(
    "--host",
    default="127.0.0.1",
    metavar="HOST",
    help="Host address to bind to.",
    show_default=True,
)
@click.option(
    "--port",
    default=8080,
    metavar="PORT",
    type=int,
    help="Port number to listen on.",
    show_default=True,
)
def cli(appname: str, host: str, port: int) -> None:
    """TiDocs: Tools for TiDB Documentation

    A suite of utilities designed to streamline TiDB documentation workflows.

    Available Applications:

        * Merge Release Notes (merge)

          Efficiently converts and combines TiDB release notes from Markdown to a well-formatted Word document.

    Examples:


        Launch the Release Notes Merger:

            $ tidocs merge

        Run with custom network settings:

            $ tidocs merge --host 0.0.0.0 --port 9000
    """
    if appname == "merge":
        pandoc = Pandoc()
        pandoc.install()
    launch_marimo_app(appname, host, port)


def main():
    try:
        cli.main(standalone_mode=False)
    except click.Abort:
        rich.print(":wave: Bye!")
    except click.ClickException:
        cli.main(["--help"], standalone_mode=False)


if __name__ == "__main__":
    main()
