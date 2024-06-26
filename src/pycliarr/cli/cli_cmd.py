import datetime
import json
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace, _SubParsersAction
from pathlib import Path
from pprint import pformat
from typing import Any, Dict, List, Optional, Union, cast, no_type_check

from pycliarr.api import base_api, base_media, exceptions, radarr, sonarr
from pycliarr.cli.utils import size_to_str


class ArgDefaults:
    CONFIG_DEFAULT = "/tmp/pycliarr_cfg.json"

    def __init__(self, config_filepath: str = CONFIG_DEFAULT):
        self.config_filepath = Path(config_filepath)
        self._op_defaults = self.load_defaults()

    def _build_key(self, obj: Any, arg: Any, default: Any) -> str:
        return f"{obj.__class__.__name__}.{arg}"

    def load_defaults(self) -> Dict[str, Any]:
        op_defaults = {}
        try:
            with open(self.config_filepath, "r") as config_file:
                op_defaults = json.load(config_file)
        except Exception:
            pass
            # print(f"Unable to load config {self.config_filepath}, ignoring presets: {e}", file=sys.stderr)
        return op_defaults

    def clear_defaults(self) -> None:
        self.config_filepath.unlink(missing_ok=True)

    def save_defaults(self):
        try:
            with open(self.config_filepath, "w") as config_file:
                json.dump(self._op_defaults, config_file)
        except Exception as e:
            print(f"Unable to save config {self.config_filepath}: {e}", file=sys.stderr)

    def to_string(self):
        return json.dumps(self._op_defaults, sort_keys=True, indent=4)

    def get_default(self, obj: Any, arg: Any, default: Any, type: Any = None) -> Any:
        key = self._build_key(obj, arg, default)
        raw_value = self._op_defaults.setdefault(key, default)
        return type(raw_value) if type and raw_value is not None else raw_value

    def set_default(self, obj: Any, arg: Any, default: Any) -> None:
        key = self._build_key(obj, arg, default)
        self.set_default_for_key(key, default)

    def set_default_for_key(self, key: str, default: Any) -> None:
        self._op_defaults[key] = str(default)


class CliCommand:
    """Base command, all command should extend this class."""

    name = ""
    description = ""

    def __init__(self) -> None:
        pass

    def set_arg_defaults(self, config_default: ArgDefaults):
        self.arg_defaults = config_default

    def add_arg_with_default(self, parser, arg, default, *args, **kwargs):
        type = bool if isinstance(default, bool) else kwargs.get("type")
        default_to_use = self.arg_defaults.get_default(self, arg, default, type=type)
        parser.add_argument(arg, *args, default=default_to_use, **kwargs)

    def configure_args(self, cmdlist_parser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = cmdlist_parser.add_parser(
            self.name, help=self.description, formatter_class=ArgumentDefaultsHelpFormatter
        )
        cmd_parser.set_defaults(cmd_name=self.name)
        return cast(ArgumentParser, cmd_parser)

    def run(self, cli: Any, args: Namespace) -> None:
        pass


class CliApiCommand:
    """Definition of an API client.

    Allows instantiating the relevant communication client, and execute a subcommmand from its name.
    """

    def __init__(self, name: str, commands: List[CliCommand]) -> None:
        self.name = name
        self.cmd_list = {cmd.name: cmd for cmd in commands}

    def add_commands_args(self, cmd_subparser: _SubParsersAction, config_default: ArgDefaults) -> None:
        for cmd in self.cmd_list:
            self.cmd_list[cmd].set_arg_defaults(config_default)
            self.cmd_list[cmd].configure_args(cmd_subparser)

    def run_command(self, cmd_name: str, args: Namespace) -> None:
        self.cmd_list[cmd_name].run(None, args)


class CliApiArrCommand(CliApiCommand):
    """Definition of an API client.

    Allows instantiating the relevant communication client, and execute a subcommmand from its name.
    """

    def __init__(self, name: str, cli_class: Any, commands: List[CliCommand]) -> None:
        super().__init__(name, commands)
        self.cli_class = cli_class

    def _new_client(self, host: str, api_key: str, username: Optional[str], password: Optional[str]) -> Any:
        cli = self.cli_class(host, api_key, username=username, password=password)
        return cli

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
        raise Exception("Invalid profile selection: {profile_id}")


def select_item(
    terms: str, choices: List[Union[radarr.RadarrMovieItem, sonarr.SonarrSerieItem]]
) -> Union[radarr.RadarrMovieItem, sonarr.SonarrSerieItem]:
    if not choices or (isinstance(choices, list) and len(choices) == 0):
        raise Exception(f"No match found for terms {terms}")
    elif issubclass(choices.__class__, base_api.BaseCliApiItem):
        # Only one result is returned
        return choices  # type: ignore
    for item in choices:
        print(f"[{choices.index(item) + 1}]: {item.title} ({item.year})")
    item_id = input(f"Select the item to add (1-{len(choices)}):")
    if item_id.isdigit() and int(item_id) <= len(choices):
        return choices[int(item_id) - 1]
    else:
        raise Exception("Invalid selection: {}")


def print_root_folder(cli: base_media.BaseCliMediaApi, raw=bool) -> None:
    res = cli.get_root_folder()
    if raw:
        print(res)
    else:
        print("Id  Free       Path")
        for root_folder in res:
            print(f"{root_folder['id']:<3} {size_to_str(root_folder.get('freeSpace')):<10} {root_folder['path']}")


def select_root_folder(cli: base_media.BaseCliMediaApi) -> int:
    print_root_folder(cli)
    root_folder_id = input("Root folder to use (Id):")
    if root_folder_id.isdigit():
        return int(root_folder_id)
    else:
        raise Exception("Invalid root folder selection, must be the folder id: {root_folder_id}")


def root_folder_id_from_arg(cli: base_media.BaseCliMediaApi, root_arg: str) -> int:
    if root_arg:
        if root_arg == "auto":
            # Interactive selection
            return select_root_folder(cli)
        elif root_arg.isdigit():
            # Id specified directly
            return int(root_arg)
        else:
            # Match the path with registered roots to find id
            res = cli.get_root_folder()
            for root_path in res:
                if root_path["path"] == root_arg:
                    return int(root_path["id"])
            raise exceptions.CliArrError(f"No root folder with path '{root_arg}'")
    return 0


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

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        self.add_arg_with_default(cmd_parser, "--page", 1, help="Page to get", type=int)
        self.add_arg_with_default(cmd_parser, "--sort-key", "progress", help="Sort key")
        self.add_arg_with_default(cmd_parser, "--page-size", 20, help="Page size", type=int)
        self.add_arg_with_default(cmd_parser, "--sort-dir", "ascending", help="Sort direction")
        self.add_arg_with_default(
            cmd_parser, "--exclude-unknown", False, help="Exclude unknown items", action="store_true"
        )
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_queue(args.page, args.sort_key, args.page_size, args.sort_dir, not args.exclude_unknown)
        print(f"{pformat(res)}\n")


class CliGetCalendarCommand(CliCommand):
    name = "calendar"
    description = "Get events from calendar"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        self.add_arg_with_default(cmd_parser, "--start", None, help="Start date, format like 2018-06-29")
        self.add_arg_with_default(cmd_parser, "--end", None, help="End date, format like 2018-06-29")
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
        self.add_arg_with_default(cmd_parser, "--page", 1, help="Page to get", type=int)
        self.add_arg_with_default(cmd_parser, "--sort-key", "airDateUtc", help="Sort key")
        self.add_arg_with_default(cmd_parser, "--page-size", 10, help="Page size", type=int)
        self.add_arg_with_default(cmd_parser, "--sort-dir", "asc", help="Sort direction")
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
        self.add_arg_with_default(cmd_parser, "--page", 1, help="Page to get", type=int)
        self.add_arg_with_default(cmd_parser, "--sort-key", "date", help="Sort key")
        self.add_arg_with_default(cmd_parser, "--page-size", 20, help="Page size", type=int)
        self.add_arg_with_default(cmd_parser, "--sort-dir", "descending", help="Sort direction")
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


class CliRootFoldersCommand(CliCommand):
    name = "root-folders"
    description = "Get root folder list"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--json", "-j", action="store_true", help="Print data as json", default=False)
        return cmd_parser

    def run(self, cli: base_media.BaseCliMediaApi, args: Namespace) -> None:
        super().run(cli, args)
        print_root_folder(cli, raw=args.json)


##############################################
########## radarr specific commands ##########
##############################################


class CliGetMovieCommand(CliCommand):
    name = "get"
    description = "Get info on a of movie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="ID of the movie to get info on", type=int, default=None)
        cmd_parser.add_argument("--json", "-j", action="store_true", help="Print data as json", default=False)
        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_movie(args.mid)
        if args.json:
            if isinstance(res, list):
                json_objs = [item.to_json() for item in res]
                print(f"[{','.join(json_objs)}]")
            else:
                print(f"{res.to_json()}")
        else:
            print(res)


class CliDeleteMovieCommand(CliCommand):
    name = "delete"
    description = "Delete a movie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="ID of the movie to delete", type=int, required=True)
        self.add_arg_with_default(
            cmd_parser, "--delfiles", False, "-f", help="Also delete files on disk", action="store_true"
        )
        self.add_arg_with_default(
            cmd_parser, "--exclude", False, "-e", help="Add exclusion from import list", action="store_true"
        )

        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.delete_movie(args.mid, delete_files=args.delfiles, add_exclusion=args.exclude)
        print(res)


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
        print(res)


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
        print(res)


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
        self.add_arg_with_default(cmd_parser, "--quality", None, "-q", help="Quality profile to use", type=int)
        cmd_parser.add_argument("--path", help="Full path where the serie should be stored", type=str, default=None)
        self.add_arg_with_default(
            cmd_parser,
            "--root-folder",
            None,
            "-r",
            help="Root folder id or path, or 'auto' to select it interactively. Ignored if --path is set",
            type=str,
        )
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
        root_id = root_folder_id_from_arg(cli, args.root_folder)

        res = cli.add_movie(
            quality=args.quality,
            tmdb_id=args.tmdb,
            imdb_id=args.imdb,
            movie_info=movie_info,  # type: ignore
            path=args.path,
            root_id=root_id,
        )
        print(f"{json.dumps(res)}")


class CliEditMovieCommand(CliCommand):
    name = "edit"
    description = "Push an updated item to the movie library"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        search_group = cmd_parser.add_mutually_exclusive_group()
        search_group.required = True
        search_group.add_argument("--json", "-j", help="json data")
        search_group.add_argument("--file", "-f", help="json file")
        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)
        json_data = args.json
        if not json_data and args.file:
            with open(args.file, "r") as f:
                json_data = f.read()
        info = radarr.RadarrMovieItem.from_json(json_data)
        res = cli.edit_movie(info)
        print(f"{json.dumps(res)}")


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


class CliSearchMissingMovies(CliCommand):
    name = "search-missing"
    description = "Search missing movies"

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.missing_movies_search()
        print(f"{json.dumps(res)}")


class CliRenameMovie(CliCommand):
    name = "get-rename"
    description = "Get renaming information if the movie can be renamed"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--mid", "-i", help="ID of the movie to get renaming info on", type=int, required=True)
        return cmd_parser

    def run(self, cli: radarr.RadarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_rename(args.mid)
        print(json.dumps(res))


##############################################
########## sonarr specific commands ##########
##############################################


class CliGetSerieCommand(CliCommand):
    name = "get"
    description = "Get info on a of serie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="ID of the serie to get info on", type=int, default=None)
        cmd_parser.add_argument("--json", "-j", action="store_true", help="Print data as json", default=False)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_serie(args.sid)
        if args.json:
            if isinstance(res, list):
                json_objs = [item.to_json() for item in res]
                print(f"[{','.join(json_objs)}]")
            else:
                print(f"{res.to_json()}")
        else:
            print(res)


class CliDeleteSerieCommand(CliCommand):
    name = "delete"
    description = "Delete a serie"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="ID of the serie to delete", type=int, required=True)
        self.add_arg_with_default(cmd_parser, "--delfiles", False, "-f", help="Also delete files on disk")
        self.add_arg_with_default(cmd_parser, "--exclude", False, "-e", help="Add exclusion from import list")
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
        self.add_arg_with_default(cmd_parser, "--quality", None, "-q", help="Quality profile to use", type=int)
        self.add_arg_with_default(
            cmd_parser, "--seasons", None, "-s", help="Comma separated list of seasons nums", type=str
        )
        self.add_arg_with_default(
            cmd_parser,
            "--season-folders",
            False,
            "-f",
            help="Whether to create season folders, default is false",
            action="store_true",
        )
        cmd_parser.add_argument("--path", help="Full path where the serie should be stored", type=str, default=None)
        self.add_arg_with_default(
            cmd_parser,
            "--root-folder",
            None,
            "-r",
            help="Root folder id or path, or 'auto' to select it interactively. Ignored if --path is set",
            type=str,
        )
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
        root_id = root_folder_id_from_arg(cli, args.root_folder)

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
            root_id=root_id,
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


class CliSearchMissingEpisodes(CliCommand):
    name = "search-missing"
    description = "Search missing episods"

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.missing_episodes_search()
        print(f"Result: {json.dumps(res)}\n")


class CliRenameEpisodes(CliCommand):
    name = "get-rename"
    description = "Get a list of episodes of a serie that can be renamed"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--sid", "-i", help="ID of the serie to list renamable files", type=int, required=True)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        res = cli.get_rename(args.sid)
        print(json.dumps(res))


##############################################
########## config specific commands ##########
##############################################
class CliConfigShowCommand(CliCommand):
    name = "show"
    description = "Display current config"

    def run(self, cli: Any, args: Namespace) -> None:
        super().run(cli, args)
        print(f"Stored config:\n{self.arg_defaults.to_string()}\n")


class CliConfigResetCommand(CliCommand):
    name = "clear"
    description = "Display current config"

    def run(self, cli: Any, args: Namespace) -> None:
        super().run(cli, args)
        self.arg_defaults.clear_defaults()
        print("Removed stored config")


class CliConfigSetCommand(CliCommand):
    name = "set"
    description = "Set a default value for the specified (Use 'show' to display available keys)"

    def configure_args(self, cmd_subparser: _SubParsersAction) -> ArgumentParser:
        cmd_parser = super().configure_args(cmd_subparser)
        cmd_parser.add_argument("--name", "-n", help="setting name", required=True)
        cmd_parser.add_argument("--value", "-v", help="setting value", required=True)
        return cmd_parser

    def run(self, cli: sonarr.SonarrCli, args: Namespace) -> None:
        super().run(cli, args)
        self.arg_defaults.set_default_for_key(args.name, args.value)
        self.arg_defaults.save_defaults()
        print(f"Config key {args.name} set to '{args.value} and stored in {self.arg_defaults.config_filepath}'\n")


#####################################################
########## Clients and commands definition ##########
#####################################################
CLI_LIST: List[CliApiCommand] = [
    CliApiArrCommand(
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
            CliSearchMissingEpisodes(),
            CliRootFoldersCommand(),
            CliRenameEpisodes(),
        ],
    ),
    CliApiArrCommand(
        "radarr",
        radarr.RadarrCli,
        [
            CliGetMovieCommand(),
            CliDeleteMovieCommand(),
            CliAddMovieCommand(),
            CliEditMovieCommand(),
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
            CliSearchMissingMovies(),
            CliRootFoldersCommand(),
            CliRenameMovie(),
        ],
    ),
    CliApiCommand(
        "config",
        [
            CliConfigResetCommand(),
            CliConfigSetCommand(),
            CliConfigShowCommand(),
        ],
    ),
]
