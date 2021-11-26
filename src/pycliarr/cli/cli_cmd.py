import datetime
import json
from argparse import ArgumentParser, Namespace, _SubParsersAction
from pprint import pformat
from typing import Any, List, Optional, Union, no_type_check

from pycliarr.api import base_api, base_media, radarr, sonarr


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


##############################################
##########  media specific commands ##########
##############################################
def select_profile(cli: base_media.BaseCliMediaApi) -> int:
    res = cli.get_quality_profiles()
    for profile in res:
        qualities = []
        for qual in profile["items"]:
            if qual["allowed"]:
                # Quality items
                if "quality" in qual:
                    qualities.append(qual["quality"]["name"])
                # Quality groups
                elif "name" in qual:
                    qualities.append(qual["name"])
        print(f"[{profile['id']}]: {profile['name']} ({qualities})")
    profile_id = input(f"Profile id to use (1-{len(res)}):")
    if profile_id.isdigit():
        return int(profile_id)
    else:
        raise Exception("Invalid profile selection: {}")


def select_language_profile(cli: base_media.BaseCliMediaApi) -> int:
    res = cli.get_language_profiles()
    for profile in res:
        print(f"[{profile['id']}]: {profile['name']}")
    profile_id = input(f"Profile id to use (1-{len(res)}):")
    if profile_id.isdigit():
        return int(profile_id)
    else:
        raise Exception("Invalid profile selection: {}")


def select_item(
    terms: str, choices: List[Union[radarr.RadarrMovieItem, sonarr.SonarrSerieItem]]
) -> Union[radarr.RadarrMovieItem, sonarr.SonarrSerieItem]:
    if not choices or (isinstance(choices, list) and len(choices) == 0):
        raise Exception(f"No match found for terms {terms}")
    elif issubclass(choices.__class__, base_api.BaseCliApiItem):
        # Only one result is returned
        return choices  # type: ignore
    for item in choices:
        print(f"[{choices.index(item)+1}]: {item.title} ({item.year})")
    item_id = input(f"Select the item to add (1-{len(choices)}):")
    if item_id.isdigit() and int(item_id) <= len(choices):
        return choices[int(item_id) - 1]
    else:
        raise Exception("Invalid selection: {}")


class CliGetProfilesCommand(CliCommand):
    name = "profiles"
    description = "Get list of quality profiles"

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_quality_profiles()
        print("Available quality profiles:\n")
        for profile in res:
            qualities = ",".join([qual["quality"]["name"] for qual in profile["items"] if qual["allowed"]])
            print(f"{profile['id']}: {profile['name']} ({qualities})")


class CliSystemStatusCommand(CliCommand):
    name = "system-status"
    description = "Get system status"

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_system_status()
        print(f"{pformat(res)}\n")


class CliGetDiskSpaceCommand(CliCommand):
    name = "disk-space"
    description = "Get disk space"

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_disk_space()
        print(f"{pformat(res)}\n")


class CliGetQueueCommand(CliCommand):
    name = "queue"
    description = "Get current downloading queue"

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_queue()
        print(f"{pformat(res)}\n")


class CliGetCalendarCommand(CliCommand):
    name = "calendar"
    description = "Get events from calendar"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--start", help="Start date, format like 2018-06-29", default=None)
        cmd_parser.add_argument("--end", help="End date, format like 2018-06-29", default=None)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        start_date = datetime.datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
        end_date = datetime.datetime.strptime(args.end, "%Y-%m-%d") if args.end else None
        res = cli.get_calendar(start_date=start_date, end_date=end_date)
        print(f"{pformat(res)}\n")


class CliDeleteQueueCommand(CliCommand):
    name = "delete-queue"
    description = "Get list of quality profiles"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, required=True)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_queue(args.id)
        print(f"{pformat(res)}\n")


class CliWantedCommand(CliCommand):
    name = "wanted"
    description = "List wanted/missing"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--page", help="Page to get", type=int, default=1)
        cmd_parser.add_argument("--sort-key", help="Sort key", default="airDateUtc")
        cmd_parser.add_argument("--page-size", help="Page size", type=int, default=10)
        cmd_parser.add_argument("--sort-dir", help="Sort direction", default="asc")
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_wanted(page=args.page, sort_key=args.sort_key, page_size=args.page_size, sort_dir=args.sort_dir)
        print(f"{pformat(res)}\n")


class CliStatusCommand(CliCommand):
    name = "status"
    description = "Get status of 1 or all currently running commands"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="command ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_command(args.id)
        print(f"{pformat(res)}\n")


class CliGetBlocklistCommand(CliCommand):
    name = "blocklist"
    description = "Get blocklisted items"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--page", help="Page to get", type=int, default=1)
        cmd_parser.add_argument("--sort-key", help="Sort key", default="date")
        cmd_parser.add_argument("--page-size", help="Page size", type=int, default=20)
        cmd_parser.add_argument("--sort-dir", help="Sort direction", default="descending")
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_blocklist(
            page=args.page, sort_key=args.sort_key, page_size=args.page_size, sort_dir=args.sort_dir
        )
        print(f"{pformat(res)}\n")


class CliDeleteBlocklistCommand(CliCommand):
    name = "delete-blocklist"
    description = "Get list of quality profiles"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_blocklist(args.id)
        print(f"{pformat(res)}\n")


class CliGetNotificationCommand(CliCommand):
    name = "notification"
    description = "Get notification(s)"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_notification(args.id)
        print(f"{pformat(res)}\n")


class CliDeleteNotificationCommand(CliCommand):
    name = "delete-notification"
    description = "Delete the specified notification or all"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, required=True)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_notification(args.id)
        print(f"{pformat(res)}\n")


class CliPutNotificationCommand(CliCommand):
    name = "put-notification"
    description = "Create the specified notification"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, required=True)
        group = cmd_parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--json", "-j", help="json data", default=None)
        group.add_argument("--file", "-f", help="json file path", default=None)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)

        # Use json data from argument by default, but load json file if specified
        if args.file:
            with open(args.file, "r") as f:
                notification_data = json.load(f)
        else:
            notification_data = json.loads(args.json)

        res = cli.put_notification(args.id, notification_data)
        print(f"{pformat(res)}\n")


class CliGetTagCommand(CliCommand):
    name = "tag"
    description = "Get tag(s)"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_tag(args.id)
        print(f"{pformat(res)}\n")


class CliGetTagDetailCommand(CliCommand):
    name = "tag-detail"
    description = "Get tag(s) details"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_tag_detail(args.id)
        print(f"{pformat(res)}\n")


class CliDeleteTagCommand(CliCommand):
    name = "delete-tag"
    description = "Delete the specified tag"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, required=True)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_tag(args.id)
        print(f"{pformat(res)}\n")


class CliEditTagCommand(CliCommand):
    name = "edit-tag"
    description = "Edit the specified tag"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, required=True)
        cmd_parser.add_argument("--label", "-l", help="tag label", type=str, required=True)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.edit_tag(args.id, args.label)
        print(f"{pformat(res)}\n")


class CliGetTagItemsCommand(CliCommand):
    name = "tag-items"
    description = "List items with specifed tag"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        group = cmd_parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--id", "-i", help="tag id", type=int, default=None)
        group.add_argument("--label", "-l", help="tag label", type=str, default=None)
        return cmd_parser

    @no_type_check
    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = None
        if args.label:
            tags = cli.get_tag_detail()
            for tag in tags:
                if tag["label"] == args.label:
                    res = tag
        else:
            res = cli.get_tag_detail(args.id)

        if res:
            print(f"Items with tag \"{res['label']}\" ({res['id']}):")
            if "seriesIds" in res:
                for tag_item in res["seriesIds"]:
                    item = cli.get_serie(tag_item)
                    print(f"    {item.title} ({item.year})")
            elif "movieIds" in res:
                for tag_item in res["movieIds"]:
                    item = cli.get_movie(tag_item)
                    print(f"    {item.title} ({item.year})")
        else:
            print("no such tag")


class CliCreateTagCommand(CliCommand):
    name = "create-tag"
    description = "Create the specified tag"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("label")
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.create_tag(args.label)
        print(f"{pformat(res)}\n")


class CliGetExclusionCommand(CliCommand):
    name = "exclusion"
    description = "Get exclusion(s)"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_exclusion(args.id)
        print(f"{pformat(res)}\n")


class CliDeleteExclusionCommand(CliCommand):
    name = "delete-exclusion"
    description = "Delete the specified exclusion"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--id", "-i", help="item ID", type=int, required=True)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_exclusion(args.id)
        print(f"{pformat(res)}\n")


##############################################
########## radarr specific commands ##########
##############################################


class CliGetMovieCommand(CliCommand):
    name = "get"
    description = "Get info on a of movie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="ID of the movie to get info on", type=int, default=None)
        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
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
            "--delfiles", "-f", help="Also delete files on disk", default=False, action="store_true"
        )
        cmd_parser.add_argument(
            "--exclude", "-e", help="Ass exclusion from import lists", default=False, action="store_true"
        )
        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_movie(args.mid, delete_files=args.delfiles, add_exclusion=args.exclude)
        print(f"Result:\n{res}")


class CliGetRefreshMovieCommand(CliCommand):
    name = "refresh"
    description = "Refresh movies"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="Movie ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.refresh_movie(args.mid)
        print(f"Result: {json.dumps(res)}\n")


class CliGetRescanMovieCommand(CliCommand):
    name = "rescan"
    description = "Rescan movies"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="Movie ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.rescan_movie(args.mid)
        print(f"Result: {json.dumps(res)}\n")


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
        cmd_parser.add_argument("--path", help="Full path where the serie should be stored", type=str, default=None)
        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)

        # If keywords were specified, look for results and prompt for choice
        movie_info = None
        if args.terms:
            choices = cli.lookup_movie(term=args.terms)
            movie_info = select_item(args.terms, choices)  # type: ignore
        # If no quality profile specified, list them qnd prompt for choice
        if not args.quality:
            args.quality = select_profile(cli)

        res = cli.add_movie(
            quality=args.quality,
            tmdb_id=args.tmdb,
            imdb_id=args.imdb,
            movie_info=movie_info,  # type: ignore
            path=args.path,
        )
        print(f"Result:\n{res}")


class CliCreateRadarrExclusionCommand(CliCommand):
    name = "create-exclusion"
    description = "Create the specified exclusion"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--title", "-t", help="title", required=True)
        cmd_parser.add_argument("--id", "-i", help="tvdb ID", type=int, required=True)
        cmd_parser.add_argument("--year", "-y", help="movie year", type=int, required=True)
        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.create_exclusion(args.title, args.id, args.year)
        print(f"{pformat(res)}\n")


##############################################
########## sonarr specific commands ##########
##############################################
class CliGetSerieCommand(CliCommand):
    name = "get"
    description = "Get info on a of serie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="ID of the serie to get info on", type=int, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_serie(args.sid)
        print(f"Serie info:\n{res}")


class CliDeleteSerieCommand(CliCommand):
    name = "delete"
    description = "Delete a serie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="ID of the serie to delete", type=int, required=True)
        cmd_parser.add_argument(
            "--delfiles", "-f", help="Also delete files on disk", default=False, action="store_true"
        )
        cmd_parser.add_argument(
            "--exclude", "-e", help="Ass exclusion from import lists", default=False, action="store_true"
        )
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_serie(args.sid, delete_files=args.delfiles, add_exclusion=args.exclude)
        print(f"Result:\n{res}")


class CliGetRefreshSerieCommand(CliCommand):
    name = "refresh"
    description = "Refresh series"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="serie ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.refresh_serie(args.sid)
        print(f"Result:\n{json.dumps(res)}\n")


class CliGetRescanSerieCommand(CliCommand):
    name = "rescan"
    description = "Rescan series"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="serie ID", type=int, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.rescan_serie(args.sid)
        print(f"Result: {json.dumps(res)}\n")


class CliAddSerieCommand(CliCommand):
    name = "add"
    description = "Add a serie from the tvdb id, or look for keywords"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        search_group = cmd_parser.add_mutually_exclusive_group()
        search_group.required = True
        search_group.add_argument("--tvdb", help="TheVideoDatabase ID of the serie to add", type=int, default=None)
        search_group.add_argument(
            "--terms", "-t", help="Keyword to search for the serie to add", type=str, default=None
        )
        cmd_parser.add_argument("--quality", "-q", help="Quality profile to use", type=int, default=None)
        cmd_parser.add_argument("--language", "-l", help="Language profile to use", type=int, default=None)
        cmd_parser.add_argument("--seasons", "-s", help="Comma separated list of seasons nums", type=str, default=None)
        cmd_parser.add_argument(
            "--season-folders",
            "-f",
            help="Whether to create season folders, default is false",
            default=False,
            action="store_true",
        )
        cmd_parser.add_argument("--path", help="Full path where the serie should be stored", type=str, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)

        # If keywords were specified, look for results and prompt for choice
        serie_info = None
        if args.terms:
            choices = cli.lookup_serie(term=args.terms)
            serie_info = select_item(args.terms, choices)  # type: ignore
        # If no quality profile specified, list them qnd prompt for choice
        if not args.quality:
            args.quality = select_profile(cli)
        if not args.language:
            args.language = select_language_profile(cli)

        # Get the optional season list
        seasons_str = args.seasons.replace(" ", "").split(",") if args.seasons else []
        try:
            seasons = [int(season_num) for season_num in seasons_str]
        except ValueError as e:
            raise Exception(f"Error, invalid season list: {args.seasons} ({e})")

        res = cli.add_serie(
            quality=args.quality,
            tvdb_id=args.tvdb,
            serie_info=serie_info,  # type: ignore
            monitored_seasons=seasons,
            season_folder=args.season_folders,
            path=args.path,
            language=args.language,
        )
        print(f"Result:\n{res}")


class CliEpisodeCommand(CliCommand):
    name = "get-episode"
    description = "Get info on an episode"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="ID of the serie to get info on", type=int, default=None)
        cmd_parser.add_argument("--epid", "-e", help="ID of the episode to get info on", type=int, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_episode(serie_id=args.sid, episode_id=args.epid)
        print(f"Episode info:\n{res}")


class CliGetEpisodeFileCommand(CliCommand):
    name = "get-episode-file"
    description = "Get info on an episode file"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="ID of the serie to get info on", type=int, default=None)
        cmd_parser.add_argument("--epid", "-e", help="ID of the episode to get info on", type=int, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_episode_file(serie_id=args.sid, episode_id=args.epid)
        print(f"Episode file:\n{res}")


class CliDeleteEpisodeFileCommand(CliCommand):
    name = "delete-episode-file"
    description = "Get info on a of serie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="ID of the serie to get info on", type=int, default=None)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_episode_file(args.sid)
        print(f"Res:\n{res}")


class CliCreateSonarrExclusionCommand(CliCommand):
    name = "create-exclusion"
    description = "Create the specified exclusion"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--title", "-t", help="title", required=True)
        cmd_parser.add_argument("--id", "-i", help="tvdb ID", type=int, required=True)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.create_exclusion(args.title, args.id)
        print(f"{pformat(res)}\n")


#####################################################
########## Clients and commands definition ##########
#####################################################
CLI_LIST: List[CliApiCommand] = [
    CliApiCommand(
        "sonarr",
        sonarr.SonarrCli,
        [
            CliGetSerieCommand(),
            CliDeleteSerieCommand(),
            CliAddSerieCommand(),
            CliGetRefreshSerieCommand(),
            CliGetRescanSerieCommand(),
            CliEpisodeCommand(),
            CliGetEpisodeFileCommand(),
            CliDeleteEpisodeFileCommand(),
            CliGetProfilesCommand(),
            CliSystemStatusCommand(),
            CliGetDiskSpaceCommand(),
            CliGetQueueCommand(),
            CliGetCalendarCommand(),
            CliDeleteQueueCommand(),
            CliWantedCommand(),
            CliStatusCommand(),
            CliGetBlocklistCommand(),
            CliDeleteBlocklistCommand(),
            CliGetNotificationCommand(),
            CliDeleteNotificationCommand(),
            CliPutNotificationCommand(),
            CliGetTagCommand(),
            CliGetTagDetailCommand(),
            CliDeleteTagCommand(),
            CliEditTagCommand(),
            CliCreateTagCommand(),
            CliGetTagItemsCommand(),
            CliGetExclusionCommand(),
            CliDeleteExclusionCommand(),
            CliCreateSonarrExclusionCommand(),
        ],
    ),
    CliApiCommand(
        "radarr",
        radarr.RadarrCli,
        [
            CliGetMovieCommand(),
            CliDeleteMovieCommand(),
            CliAddMovieCommand(),
            CliGetRefreshMovieCommand(),
            CliGetRescanMovieCommand(),
            CliGetProfilesCommand(),
            CliSystemStatusCommand(),
            CliGetDiskSpaceCommand(),
            CliGetQueueCommand(),
            CliGetCalendarCommand(),
            CliDeleteQueueCommand(),
            CliWantedCommand(),
            CliStatusCommand(),
            CliGetBlocklistCommand(),
            CliDeleteBlocklistCommand(),
            CliGetNotificationCommand(),
            CliDeleteNotificationCommand(),
            CliPutNotificationCommand(),
            CliGetTagCommand(),
            CliGetTagDetailCommand(),
            CliDeleteTagCommand(),
            CliEditTagCommand(),
            CliCreateTagCommand(),
            CliGetTagItemsCommand(),
            CliGetExclusionCommand(),
            CliDeleteExclusionCommand(),
            CliCreateRadarrExclusionCommand(),
        ],
    ),
]
