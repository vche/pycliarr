from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from pycliarr.api.base_api import BaseCliApiItem, json_data
from pycliarr.api.base_media import BaseCliMediaApi
from pycliarr.api.exceptions import SonarrCliError


class SonarrSerieItem(BaseCliApiItem):
    """Class for handling serie info."""

    def _model(self) -> Dict[Any, Any]:
        """Define the model of items represented by this class."""
        return {
            "title": "",
            "alternateTitles": [],
            "sortTitle": "",
            "statistics": {},
            "status": "",
            "overview": "",
            "network": "",
            "airTime": "",
            "images": [],
            "seasons": [],
            "year": 0,
            "path": "",
            "seasonFolder": True,
            "monitored": True,
            "useSceneNumbering": False,
            "runtime": 0,
            "tvdbId": 0,
            "tvRageId": 0,
            "tvMazeId": 0,
            "firstAired": "",
            "seriesType": "",
            "cleanTitle": "",
            "imdbId": "",
            "titleSlug": "",
            "certification": "",
            "genres": [],
            "tags": [],
            "added": "",
            "ratings": {},
            "qualityProfileId": 0,
            "id": 0,
        }


class SonarrCli(BaseCliMediaApi):
    """Sonarr api client.

    API reference:
        https://github.com/Sonarr/Sonarr/wiki/API
        https://pub.dev/packages/sonarr

    Note:
        Not all commands are implemented.
        Some commands available are implemented in BaseCliMediaApi:
        * get_calendar
        * get_command
        * get_quality_profiles
        * get_disk_space
        * get_system_status
        * get_queue
        * delete_queue

    Todo:
        * get_wanted
        * get_logs
        * get_backup
        * get_episode_files
        * delete_episode_files
        * search_selected
    """

    # Set api specific to radarr (differs from the default ones in BaseCliMediaApi)
    api_url_item = f"{BaseCliMediaApi.api_url_base}/series"
    api_url_itemlookup = f"{BaseCliMediaApi.api_url_base}/series/lookup"
    api_url_episode = f"{BaseCliMediaApi.api_url_base}/episode"
    api_url_episodefile = f"{BaseCliMediaApi.api_url_base}/episodefile"

    # Keep using v1 for commands not available in v3
    api_url_wanted_missing = "/api/wanted/missing"

    def get_serie(self, serie_id: Optional[int] = None) -> Union[SonarrSerieItem, List[SonarrSerieItem]]:
        """Get specified serie, or all if no id provided from server collection.

        Args:
            serie_id (Optional[int]) ID of serie to get, all items by default
        Returns:
            ``SonarrSerieItem`` if a serie id is specified, or a list of ``SonarrSerieItem``
        """
        res = self.get_item(serie_id)
        if isinstance(res, list):
            return [SonarrSerieItem.from_dict(serie) for serie in res]
        else:
            return SonarrSerieItem.from_dict(res)

    def lookup_serie(
        self, term: Optional[str] = None, tvdb_id: Optional[int] = None
    ) -> Optional[Union[SonarrSerieItem, List[SonarrSerieItem]]]:
        """Search for a serie based on keyword, or tvdb id.

        If tvdb id is provided, it will be used. If not, the keywords will be used.
        One of ``term``, or ``tvdb_id`` must be specified.

        Args:
            term (Optional[str]): Keywords to seach for
            tvdb_id (Optional[str]): TVDB serie id
        Returns:
            json response
        """
        if tvdb_id:
            term = "tvdb:" + str(tvdb_id)
        elif not term:
            raise SonarrCliError("Error invalid parameters")

        res = self.lookup_item(str(term))
        if not res:
            return None
        elif isinstance(res, list):
            if len(res) > 1:
                return [SonarrSerieItem.from_dict(serie) for serie in res]
            else:
                res = res[0]
        return SonarrSerieItem.from_dict(res)

    def add_serie(
        self,
        quality: int,
        tvdb_id: Optional[int] = None,
        serie_info: Optional[SonarrSerieItem] = None,
        monitored_seasons: List[int] = [],
        monitored: bool = True,
        search: bool = True,
        season_folder: bool = True,
        path: Optional[str] = None,
        root_id: int = 0,
    ) -> json_data:
        """addMovie adds a new serie to collection.

        The serie description serie_info must be specified. If the IMDB or TMDB id is provided instead,
        it will be used to fetch the required serie description from TMDB.

        Args:
            quality: Quality profile to use, as retrieved by get_quality_profiles()
            tvdb_id (Optional[int]): TVDB id of the serie to add
            serie_info (Optional[RadarrserieItem]): Description of the serie to add
            monitored_seasons: Optional list of seasons numbers to monitor. Latest season only by default.
            monitored (bool): Whether to monitor the serie. Default is True
            search (bool): Whether to search for the serie once added. Default is True
            season_folder (bool): If True (default), create a folder for each season.
            path (Optional[str]): Specify the path awhere the movie should be stored. Default is root/<serie name>.
            root_id (Optional[int]): Specify the root folder to use. Ignored if a path is specified. Default is root[0].

        Returns:
            json response

        Note: To further customize the parameters of the serie to add, manually look it up
        Example:
            info = sonarr.lookup_serie(tvdb_id=tvdb_id)
            info["seasons"] = {"seasonNumber": 1, "monitored": False}
            sonarr.add_serie(quality: 1, serie_info: info)
        """
        # Get info from imdb/tvdb if needed:
        if tvdb_id:
            serie_info = cast(SonarrSerieItem, self.lookup_serie(tvdb_id=tvdb_id))
        if not serie_info:
            raise SonarrCliError("Error, invalid parameters or invalid tvdb id")

        # Prepare serie info for adding
        serie_info.path = path or str(self.build_serie_path(serie_info, root_folder_id=root_id))
        serie_info.qualityProfileId = quality
        serie_info.monitored = monitored
        serie_info.seasonFolder = season_folder

        # Specifically monitors only the specified seasons
        if monitored_seasons:
            for season in serie_info.seasons:
                season["monitored"] = season["seasonNumber"] in monitored_seasons

        options = {
            "searchForMissingEpisodes": search,
            "ignoreEpisodesWithFiles": True,
            "ignoreEpisodesWithoutFiles": False if monitored_seasons else True,
        }
        serie_info.add_attribute("addOptions", options)

        return self.add_item(json_data=serie_info.to_dict())

    def build_serie_path(self, serie_info: SonarrSerieItem, root_folder_id: int = 0) -> Path:
        """Build a serie folder path using the root folder specified.
        Args:
            serie_info (SonarrSerieItem) Item for which to build the path
            root_folder_id (int): Id of the root folder (can be retrieved with get_root_folder()).
            If the id is not found or not specified, the first root folder in the list is used.

        Returns: Full path of the serie in the format <root path>/<serie name>
        """
        return self.build_item_path(serie_info.title, root_folder_id)

    def delete_serie(self, serie_id: int, delete_files: bool = True, add_exclusion: bool = False) -> json_data:
        """Delete the serie with the given ID

        Args:
            serie_id (int):  Serie to delete
            delete_files (bool): Optional. Also delete files. Default is True
            add_exclusion: Optionally exclude the serie from further tvdb auto add
        Returns:
            json response
        """
        options = {"addImportListExclusion": add_exclusion} if add_exclusion else {}
        return self.delete_item(serie_id, delete_files, options)

    def edit_serie(self, serie_info: SonarrSerieItem) -> json_data:
        """Edit a serie from the collection.

        The serie description movie_info must be specified, usually by getting the information from get_serie()

        Args:
            serie_info (Optional[RadarrMovieItem]): Description of the movie to edit
        Returns:
            json response
        """

        return self.edit_item(json_data=serie_info.to_dict())

    def refresh_serie(self, serie_id: Optional[int] = None) -> json_data:
        """Refresh serie information  and rescan disk.

        Args:
            serie_id (Optional[int]): serie to refresh, if not set all series will be refreshed and scanned
        Returns:
            json response
        """
        data: Dict[str, Any] = {"name": "RefreshSeries"}
        if serie_id:
            data["seriesId"] = serie_id
        return self._sendCommand(data)

    def rescan_serie(self, serie_id: Optional[int] = None) -> json_data:
        """Scan disk for any downloaded serie for all or specified serie.

        Args:
            serie_id (Optional[int]): serie to refresh, if not set all series will be refreshed and scanned
        Returns:
            json response
        """
        data: Dict[str, Any] = {"name": "RescanSeries"}
        if serie_id:
            data["seriesId"] = serie_id
        return self._sendCommand(data)

    def get_episode(
        self, serie_id: Optional[int] = None, episode_id: Optional[int] = None
    ) -> Union[json_data, List[json_data]]:
        """Returns specified episode or all for the given serie

        Args:
            serie_id (int): ID of the serie to get all episodes from
            episode_id (int): ID of a specific episode to get
        Returns:
            json response
        """
        if serie_id:
            res = self.request_get(self.api_url_episode, url_params={"seriesId": serie_id})
        elif episode_id:
            res = self.request_get(f"{self.api_url_episode}/{episode_id}")
        else:
            raise SonarrCliError("serie_id or episode_id must be provided")
        return res

    def get_episode_file(
        self, serie_id: Optional[int] = None, episode_id: Optional[int] = None
    ) -> Union[json_data, List[json_data]]:
        """Returns specified episode file or all for the given serie

        Args:
            serie_id (int): ID of the serie to get all episodes files from
            episode_id (int): ID of a specific episode file to get
        Returns:
            json response
        """
        if serie_id:
            res = self.request_get(self.api_url_episodefile, url_params={"seriesId": serie_id})
        elif episode_id:
            res = self.request_get(f"{self.api_url_episodefile}/{episode_id}")
        else:
            raise SonarrCliError("serie_id or episode_id must be provided")
        return res

    def delete_episode_file(self, episode_id: int) -> json_data:
        """Delete the given episode file

        Args:
            episode_id (int): ID of the episode to delete
        Returns:
            json response
        """
        return self.request_delete(f"{self.api_url_episodefile}/{episode_id}")

    def create_exclusion(self, title: str, tvdb_id: int) -> json_data:
        """Create the specified exclusions

        Args:
            item_id (int):  id of the exclusions to create
        Returns:
            json response
        """
        return self.request_post(self.api_url_exclusions, json_data={"title": title, "tvdbId": tvdb_id})

    def missing_episodes_search(self) -> json_data:
        """Search for missing episodes.
        Returns:
            json response
        """
        return self._sendCommand({"name": "missingEpisodeSearch"})

    def get_queue(
        self,
        page: int = 1,
        sort_key: str = "progress",
        page_size: int = 20,
        sort_dir: str = "ascending",
        include_unknown: bool = True,
    ) -> json_data:
        """Get queue info (downloading/completed, ok/warning) as json

        Args:
            page (int) - 1-indexed (1 default)
            sort_key (string) - title or date
            page_size (int) - Default: 10
            sort_dir (string) - asc or desc - Default: asc
            options (Dict[str, Any]={}): Optional additional options
        """
        return self._get_queue(
            page, sort_key, page_size, sort_dir, options={"includeUnknownSeriesItems": include_unknown}
        )

    def rename_files(self, file_ids: List[int], serie_id: int) -> json_data:
        """Rename the list of files provided.

        Args:
            file_ids (List[int]): List of ids of files to rename
            serie_id int: The id of the series to rename
        Returns:
            json response
        """
        return self._sendCommand(
            {
                "name": "RenameFiles",
                "files": file_ids,
                "seriesId": serie_id,
            }
        )

    def get_rename(self, serie_id: int) -> json_data:
        """Get a list of episodes files that can be renamed

        Args:
            serie_id (int):  id of the serie of which to get the renamable episodes
        Returns:
            json response
        """
        return self.request_get(self.api_url_rename, url_params={"seriesId": serie_id})
