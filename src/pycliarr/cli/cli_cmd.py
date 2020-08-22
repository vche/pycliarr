from argparse import ArgumentParser, Namespace, _SubParsersAction
from typing import Any, List, Optional

from pycliarr.api import sonarr


class CliCommand:
    """Base command, all command should extend this class."""

    name = ""
    description = ""

    def __init__(self) -> None:
        pass

    def configure_args(self, cmdlist_parser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = cmdlist_parser.add_parser(self.name, help=self.description)
        cmd_parser.set_defaults(cmd_name=self.name)
        return cmd_parser

    def run(self, cli: Any, args: Namespace) -> None:
        pass


class CliApiCommand:
    """Definition of an API client.

    Allows instantiating the relevant communication client, and execute a subcommmand from its name.
    """

    def __init__(self, name: str, cli_class: Any, commands: List[CliCommand]) -> None:
        self.name = name
        self.cli_class = cli_class
        self.cmd_list = {cmd.name: cmd for cmd in commands}

    def _new_client(self, host: str, api_key: str, username: Optional[str], password: Optional[str]) -> Any:
        cli = self.cli_class(host, api_key, username=username, password=password)
        return cli

    def add_commands_args(self, cmd_subparser: _SubParsersAction) -> None:
        for cmd in self.cmd_list:
            self.cmd_list[cmd].configure_args(cmd_subparser)

    def run_command(self, cmd_name: str, args: Namespace) -> None:
        cli = self._new_client(args.host, args.api_key, username=args.user, password=args.password)
        self.cmd_list[cmd_name].run(cli, args)


class CliListMoviesCommand(CliCommand):
    name = "list"
    description = "Get list of movies"

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.list()
        print(f"Movie list:\n{res}")


class CliGetMovieCommand(CliCommand):
    name = "get"
    description = "Get info on a of movie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="ID of the movie to get info on", required=True)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_movie(args.mid)
        print(f"Movie {args.mid} info:\n{res}")


# Declare the list of api clients here, and the list of commands they can accept from the CLI
CLI_LIST: List[CliApiCommand] = [
    CliApiCommand("sonarr", sonarr.SonarrCli, [CliListMoviesCommand(), CliGetMovieCommand()]),
]
