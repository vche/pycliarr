from argparse import ArgumentParser, Namespace, _SubParsersAction
from pprint import pformat
from typing import Any, List, Optional
import datetime
from pycliarr.api import radarr, sonarr


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


class CliGetProfilesCommand(CliCommand):
    name = "profiles"
    description = "Get list of quality profiles"

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_quality_profiles()
        print("Available quality profiles:\n")
        for profile in res:
            qualities = ",".join([qual["quality"]["name"] for qual in profile["items"] if qual["allowed"]])
            print(f"{profile['id']}: {profile['name']} ({qualities})")


class CliGetMovieCommand(CliCommand):
    name = "get"
    description = "Get info on a of movie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="ID of the movie to get info on", type=int, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_movie(args.mid)
        print(f"Movie info:\n{res}")


class CliDeleteMovieCommand(CliCommand):
    name = "delete"
    description = "Delete a movie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="ID of the movie to delete", type=int, required=True)
        cmd_parser.add_argument(
            "--delfiles", "-d", help="Also delete files on disk", default=False, action="store_true"
        )
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_movie(args.mid, delete_files=args.delfiles)
        print(f"Result:\n{res}")


class CliSystemStatusCommand(CliCommand):
    name = "system-status"
    description = "Get system status"

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_system_status()
        print(f"System status: {pformat(res)}\n")


class CliGetDiskSpaceCommand(CliCommand):
    name = "disk-space"
    description = "Get disk space"

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_disk_space()
        print(f"Disk space: {pformat(res)}\n")


class CliGetQueueCommand(CliCommand):
    name = "queue"
    description = "Get current downloading queue"

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_queue()
        print(f"Queue: {pformat(res)}\n")


class CliGetRefreshMovieCommand(CliCommand):
    name = "refresh"
    description = "Get list of quality profiles"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="Movie ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.refresh_movie(args.mid)
        print(f"Result: {res}\n")


class CliGetRescanMovieCommand(CliCommand):
    name = "rescan"
    description = "Get list of quality profiles"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="Movie ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.rescan_movie(args.mid)
        print(f"Result: {res}\n")


class CliGetCalendarCommand(CliCommand):
    name = "calendar"
    description = "Get events from calendar"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--start", help="Start date, format like 2018-06-29", default=None)
        cmd_parser.add_argument("--end", help="End date, format like 2018-06-29", default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        start_date = datetime.datetime.strptime(args.start, '%Y-%m-%d') if args.start else None
        end_date = datetime.datetime.strptime(args.end, '%Y-%m-%d') if args.end else None
        res = cli.get_calendar(start_date=start_date, end_date=end_date)
        print(f"Calendar events: {res}\n")


class CliDeleteQueueCommand(CliCommand):
    name = "delqueue"
    description = "Get list of quality profiles"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="Movie ID", type=int, required=True)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_queue()
        print(f"Result: {res}\n")


class CliAddMovieCommand(CliCommand):
    name = "add"
    description = "Add a movie from the imdb/tmdb id, or look for keywords"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        search_group = cmd_parser.add_mutually_exclusive_group()
        search_group.required = True
        search_group.add_argument("--tmdb", help="TheMovieDatabase ID of the movie to add", type=int, default=None)
        search_group.add_argument("--imdb", help="IMDB ID of the movie to add", type=str, default=None)
        search_group.add_argument(
            "--terms", "-t", help="Keyword to search for the movie to add", type=str, default=None
        )
        cmd_parser.add_argument("--quality", "-q", help="Quality profile to use", type=int, default=None)
        return cmd_parser

    def select_profile(self, cli: sonarr.SonarrCli):
        res = cli.get_quality_profiles()
        for profile in res:
            qualities = ",".join([qual["quality"]["name"] for qual in profile["items"] if qual["allowed"]])
            print(f"[{profile['id']}]: {profile['name']} ({qualities})")
        profile_id = input(f"Profile id to use (1-{len(res)}):")
        if profile_id.isdigit() and int(profile_id) <= len(res):
            return int(profile_id)
        else:
            raise Exception("Invalid profile selection: {}")

    def select_movie(self, cli: sonarr.SonarrCli, terms: str):
        choices = cli.lookup_movie(term=terms)
        if len(choices) == 0:
            raise Exception(f"No match found for terms {terms}")
        for movie in choices:
            print(f"[{choices.index(movie)+1}]: {movie.title} ({movie.year})")
        movie_id = input(f"Select the movie to add (1-{len(choices)}):")
        if movie_id.isdigit() and int(movie_id) <= len(choices):
            return choices[int(movie_id)-1]
        else:
            raise Exception("Invalid movie selection: {}")

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)

        # If keywords were specified, look for results and prompt for choice
        movie_info = None
        if args.terms:
            movie_info = self.select_movie(cli, args.terms)
        # If no quality profile specified, list them qnd prompt for choice
        if not args.quality:
            args.quality = self.select_profile(cli)

        res = cli.add_movie(quality=args.quality, tmdb_id=args.tmdb, imdb_id=args.imdb, movie_info=movie_info)
        print(f"Result:\n{res}")


# Declare the list of api clients here, and the list of commands they can accept from the CLI
CLI_LIST: List[CliApiCommand] = [
    CliApiCommand("sonarr", sonarr.SonarrCli, [CliGetProfilesCommand(), CliGetMovieCommand()]),
    CliApiCommand(
        "radarr",
        radarr.RadarrCli,
        [
            CliGetProfilesCommand(),
            CliGetMovieCommand(),
            CliDeleteMovieCommand(),
            CliAddMovieCommand(),
            CliSystemStatusCommand(),
            CliGetDiskSpaceCommand(),
            CliGetQueueCommand(),
            CliGetCalendarCommand(),
            CliGetRefreshMovieCommand(),
            CliGetRescanMovieCommand(),
            CliDeleteQueueCommand(),
        ],
    ),
]
