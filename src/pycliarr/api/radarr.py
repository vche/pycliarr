from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from pycliarr.api.base_api import BaseCliApiItem, json_data, json_list
from pycliarr.api.base_media import BaseCliMediaApi
from pycliarr.api.exceptions import RadarrCliError


class RadarrMovieItem(BaseCliApiItem):
    """Class for handling movie info."""

    def _model(self) -> Dict[Any, Any]:
        """Define the model of items represented by this class."""
        return {
            "title": "",
            "originalTitle": "",
            "sortTitle": "",
            "sizeOnDisk": 0,
            "overview": "",
            "inCinemas": None,
            "physicalRelease": None,
            "status": "",
            "images": [],
            "website": "",
            "downloaded": False,
            "year": 0,
            "hasFile": False,
            "youTubeTrailerId": "",
            "studio": "",
            "path": "",
            "rootFolderPath": "",
            "monitored": True,
            "minimumAvailability": "",
            "isAvailable": "",
            "folderName": "",
            "runtime": 0,
            "cleanTitle": "",
            "imdbId": "",
            "tmdbId": 0,
            "titleSlug": "",
            "certification": "",
            "genres": [],
            "tags": [],
            "added": None,
            "ratings": {},
            "collection": {},
            "alternateTitles": [],
            "qualityProfileId": 0,
            "secondaryYearSourceId": 0,
            "id": 0,
        }


class RadarrCli(BaseCliMediaApi):
    """Radar api client.

    Radarr API reference:
        https://github.com/Radarr/Radarr/wiki/API
        https://pub.dev/packages/radarr

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
        * get_history
        * get_logs
        * get_wanted
        * get_blocklist
        * delete_blocklist
    """

    # Set api specific to radarr (differs from the default ones in BaseCliMediaApi)
    api_url_item = f"{BaseCliMediaApi.api_url_base}/movie"
    api_url_itemlookup = f"{BaseCliMediaApi.api_url_base}/movie/lookup"
    api_url_exclusions = f"{BaseCliMediaApi.api_url_base}/exclusions"
    api_url_language_profile = f"{BaseCliMediaApi.api_url_base}/languageProfile"

    # Keep using v1 for commands not available in v3
    api_url_wanted_missing = "/api/wanted/missing"

    def get_language_profiles(self) -> json_list:
        """Return the quality profiles"""
        return cast(json_list, self.request_get(self.api_url_language_profile))

    def get_movie(self, movie_id: Optional[int] = None) -> Union[RadarrMovieItem, List[RadarrMovieItem]]:
        """Get specified movie, or all if no id provided from server collection.

        Args:
            movie_id (Optional[int]) ID of movie to get, all items by default
        Returns:
            ``RadarrMovieItem`` if a movie id is specified, or a list of ``RadarrMovieItem``
        """
        res = self.get_item(movie_id)
        if isinstance(res, list):
            return [RadarrMovieItem.from_dict(movie) for movie in res]
        else:
            return RadarrMovieItem.from_dict(res)

    def lookup_movie(
        self, term: Optional[str] = None, imdb_id: Optional[str] = None, tmdb_id: Optional[int] = None
    ) -> Optional[Union[RadarrMovieItem, List[RadarrMovieItem]]]:
        """Search for a movie based on keyword, or imbd/tmdb id.

        If no imdb id is provided, tvdb id will be used. If neither of them is provided, the keyword will be used.
        One of ``term``, ``imdb_id``, or ``tmdb_id`` must be specified.

        Args:
            term (Optional[str]): Keywords to seach for
            imdb_id (Optional[str]): IMDB movie id
            tmdb_id (Optional[int]): TMDB movie id
        Returns:
            json response
        """
        if tmdb_id:
            term = "tmdb:" + str(tmdb_id)
        elif imdb_id:
            term = "imdb:" + str(imdb_id)
        elif not term:
            raise RadarrCliError("Error, invalid parameters")

        res = self.lookup_item(str(term))
        if not res:
            return None
        elif isinstance(res, list):
            if len(res) > 1:
                return [RadarrMovieItem.from_dict(movie) for movie in res]
            else:
                res = res[0]
        return RadarrMovieItem.from_dict(res)

    def add_movie(
        self,
        quality: int,
        tmdb_id: Optional[int] = None,
        imdb_id: Optional[str] = None,
        movie_info: Optional[RadarrMovieItem] = None,
        monitored: bool = True,
        search: bool = True,
        path: Optional[str] = None,
        root_id: int = 0,
    ) -> json_data:
        """addMovie adds a new movie to collection.

        The movie description movie_info must be specified. If the IMDB or TMDB id is provided instead,
        it will be used to fetch the required movie description from TMDB.

        Args:
            quality: Quality profile to use, as retrieved by get_quality_profiles()
            imdbp_id (Optional[int]): IMDB id of the movie to add
            tmdb_id (Optional[int]): TMDB id of the movie to add
            movie_info (Optional[RadarrMovieItem]): Description of the movie to add
            monitored (bool): Whether to monitor the movie. Default is True
            search (bool): Whether to search for the movie once added. Default is True
            path (Optional[str]): Specify the path awhere the movie should be stored.
                Default is root[0]/<movie name> (<movie year>).
            root_id (Optional[int]): Specify the root folder to use. Ignored if a path is specified. Default is root[0].
        Returns:
            json response
        """

        # Get info from imdb/tmdb if needed:
        if tmdb_id or imdb_id:
            movie_info = cast(RadarrMovieItem, self.lookup_movie(tmdb_id=tmdb_id, imdb_id=imdb_id))
        if not movie_info:
            raise RadarrCliError("Error, invalid parameters or invalid tmdb/imdb id")

        # Prepare movie info for adding
        movie_info.path = path or str(self.build_movie_path(movie_info, root_folder_id=root_id))
        movie_info.qualityProfileId = quality
        movie_info.monitored = monitored
        movie_info.add_attribute("addOptions", {"searchForMovie": search})

        return self.add_item(json_data=movie_info.to_dict())

    def build_movie_path(self, movie_info: RadarrMovieItem, root_folder_id: int = 0) -> Path:
        """Build a movie folder path using the root folder specified.
        Args:
            serie_info (SonarrSerieItem) Item for which to build the path
            root_folder_id (int): Id of the root folder (can be retrieved with get_root_folder())
            If the id is not found or not specified, the first root folder in the list is used.

        Returns: Full path of the serie in the format <root path>/<movie name> (<movie year>)
        """
        return self.build_item_path(
            movie_info.title + (f" ({movie_info.year})" if movie_info.year else ""), root_folder_id
        )

    def delete_movie(self, movie_id: int, delete_files: bool = True, add_exclusion: bool = False) -> json_data:
        """Delete the movie with the given ID

        Args:
            movie_id (int):  Movie to delete
            delete_files (bool): Optional. Also delete files. Default is True
            add_exclusion: Optionally exclude the movie from further imdb/tmdb auto add
        Returns:
            json response
        """
        options = {"addImportExclusion": add_exclusion} if add_exclusion else {}
        return self.delete_item(movie_id, delete_files, options)

    def edit_movie(
        self,
        movie_info: RadarrMovieItem,
        move_files: bool = False,
    ) -> json_data:
        """Edit a movie from the collection.

        The movie description movie_info must be specified, usually by getting the information from get_movie()

        Args:
            movie_info (Optional[RadarrMovieItem]): Description of the movie to edit
            move_files (bool): Whether to move files after edition. Default is False
        Returns:
            json response
        """

        return self.edit_item(json_data=movie_info.to_dict())  # , url_params={"moveFiles": False})

    def refresh_movie(self, movie_id: Optional[int] = None) -> json_data:
        """Refresh movie information  and rescan disk.

        Args:
            movie_id (Optional[int]): Movie to refresh, if not set all movies will be refreshed and scanned
        Returns:
            json response
        """
        data: Dict[str, Any] = {"name": "RefreshMovie"}
        if movie_id:
            data["movieId"] = movie_id
        return self._sendCommand(data)

    def rescan_movie(self, movie_id: Optional[int] = None) -> json_data:
        """Scan disk for any downloaded movie for all or specified movie.

        Args:
            movie_id (Optional[int]): Movie to refresh, if not set all movies will be refreshed and scanned
        Returns:
            json response
        """
        data: Dict[str, Any] = {"name": "RescanMovie"}
        if movie_id:
            data["movieId"] = movie_id
        return self._sendCommand(data)

    def create_exclusion(self, title: str, tmdb_id: int, year: int) -> json_data:
        """Create the specified exclusions

        Args:
            item_id (int):  id of the exclusions to create
        Returns:
            json response
        """
        return self.request_post(
            self.api_url_exclusions, json_data={"movieTitle": title, "tmdbId": tmdb_id, "movieYear": year}
        )

    def missing_movies_search(self) -> json_data:
        """Search for missing movies.
        Returns:
            json response
        """
        return self._sendCommand({"name": "MissingMoviesSearch"})

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
            page, sort_key, page_size, sort_dir, options={"includeUnknownMovieItems": include_unknown}
        )

    def rename_files(self, file_ids: List[int]) -> json_data:
        """Rename the list of files provided.

        Args:
            file_ids (List[int]): List of ids of files to rename
        Returns:
            json response
        """
        return self._sendCommand({"name": "RenameFiles", "files": file_ids})

    def get_rename(self, movie_id: int) -> json_data:
        """Get the possible renaming for the specified movie

        Args:
            movie_id (int):  id of the movie to check
        Returns:
            json response
        """
        return self.request_get(self.api_url_rename, url_params={"movieId": movie_id})
