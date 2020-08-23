import logging
import sys
import traceback
from argparse import ArgumentParser, Namespace
from typing import Dict, List

import pycliarr
from pycliarr.api import exceptions
from pycliarr.cli import utils
from pycliarr.cli.cli_cmd import CLI_LIST, CliApiCommand

log = logging.getLogger(__name__)


def _parse_args(cli_mapping: Dict[str, CliApiCommand]) -> Namespace:
    """
    cliarr host api-key sonarr list/get/delete/add
    cliarr host api-key radarr list/get/delete/add
    """
    parser = ArgumentParser(description="Radarr/Sonarr client")

    parser.add_argument("--host", "-t", help="Host url, e.g 'http://192.168.0.1'", required=True)
    parser.add_argument("--api-key", "-k", help="API key, e.g '5f5e32xf3ff8463d9f1d2u88ef0fd3e8'", required=True)
    parser.add_argument("--user", "-u", help="Username if using basic authentication", default=None)
    parser.add_argument("--password", "-p", help="Password if using basic authentication", default=None)
    parser.add_argument("--debug", "-d", default=False, action="store_true", help="Enable debug logging")
    client_subparser = parser.add_subparsers(dest="client")
    client_subparser.required = True

    # Add a client
    for cli in cli_mapping:
        client_parser = client_subparser.add_parser(cli, help=f"use {cli} client")
        client_parser.set_defaults(cli_name=cli)
        cmd_subparser = client_parser.add_subparsers(dest=f"{cli} command")
        cmd_subparser.required = True
        cli_mapping[cli].add_commands_args(cmd_subparser)

    args = parser.parse_args()
    args.log_level = logging.DEBUG if args.debug else logging.INFO

    return args


def _run_command(cli_mapping: Dict[str, CliApiCommand], cli_name: str, cmd_name: str, args: Namespace) -> None:
    """Execute a command from the client name and the command name."""
    cli_mapping[cli_name].run_command(cmd_name, args)


def _build_mapping(cli_list: List[CliApiCommand]) -> Dict[str, CliApiCommand]:
    """Build a mapping to get an api client entry from its name."""
    return {cli.name: cli for cli in cli_list}


def main() -> None:
    """Main entry point."""
    print(f"PyCliarr version {pycliarr.__version__}")

    cli_mapping = _build_mapping(CLI_LIST)
    args = _parse_args(cli_mapping)
    utils.setup_logging(level=args.log_level)

    try:
        _run_command(cli_mapping, args.cli_name, args.cmd_name, args)
        sys.exit(0)
    except exceptions.CliArrError as e:
        print(f"API error: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(2)
