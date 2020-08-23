from typing import Any, Dict, List, Optional, Union

from pycliarr.api.base_api import BaseCliApiItem
from pycliarr.api.base_media import BaseCliMediaApi


class RadarrMovieItem(BaseCliApiItem):
    """Class for handling movie info."""

    def _model(self) -> Dict[Any, Any]:
        """Define the model of items represented by this class."""
        return {
            "title": "",
            "sortTitle": "",
            "sizeOnDisk": 0,
            "status": "",
            "images": [],
            "downloaded": False,
            "year": 0,
            "hasFile": False,
            "path": "",
            "profileId": 0,
            "monitored": True,
            "minimumAvailability": "",
            "runtime": 0,
            "cleanTitle": "",
            "imdbId": "",
            "tmdbId": 0,
            "titleSlug": "",
            "genres": [],
            "tags": [],
            "added": "",
            "alternativeTitles": [],
            "qualityProfileId": 0,
            "id": 0
        }


class RadarrCli(BaseCliMediaApi):
    """Radar api client.

    API reference: https://github.com/Radarr/Radarr/wiki/API

    Note: Not all commands are implemented.
    Some commands available are implemented in BaseCliMediaApi:
    - get_calendar
    - get_command
    - get_quality_profiles
    - rename_files
    - get_disk_space
    - get_system_status
    - get_queue
    - delete_queue
    """

    # Set api specific to radarr (differs from the default ones in BaseCliMediaApi)
    api_url_item = "/api/movie"
    api_url_itemlookup = "/api/movie/lookup"

    def get_movie(self, movie_id: Optional[int]) -> Union[RadarrMovieItem, List[RadarrMovieItem]]:
        res = self.get_item(movie_id)
        if isinstance(res, list):
            return [RadarrMovieItem.from_dict(movie) for movie in res]
        else:
            return RadarrMovieItem.from_dict(res)

    def lookup_movie(self, term: Optional[str] = None, imdb_id: Optional[str] = None, tmdb_id: Optional[str] = None):
        """Search for a movie based on keyword, or imbd/tmdb id.

        If no imdb id is provided, tvdb id will be used. If neither of them is provided, the keyword will be used.
        One of term, imdb_id, or tmdb_id must be specified.

        Args:
            term (Optional[str]): Keywords to seach for
            imdb_id (Optional[str]): IMDB movie id
            tmdb_id (Optional[str]): TVDB movie id
        Returns:
            json response
        """
        term = str(term)
        if tmdb_id:
            url_path = f"{self.api_url_itemlookup}/tmdb"
            url_params = {"tmdbId": tmdb_id}
            res = self.request_get(url_path, url_params=url_params)
        elif imdb_id:
            url_path = f"{self.api_url_itemlookup}/imdb"
            url_params = {"imdbId": imdb_id}
            res = self.request_get(url_path, url_params=url_params)
        elif term:
            res = self.lookup_item(term)

        return [RadarrMovieItem.from_dict(movie) for movie in res]

    def add_movie(
        self,
        quality: int,
        tmdb_id: Optional[int] = None,
        imdb_id: Optional[int] = None,
        movie_info: Optional[RadarrMovieItem] = None,
        monitored: bool = True,
        search: bool = True,
    ):
        """addMovie adds a new movie to collection.

        The movie description movie_info must be specified. If the IMDB or TMDB id is provided instead,
        it will be used to fetch the required movie description from TMDB.
        Args:
            quality: Quality profile to use, as retrieved by get_quality_profiles()
            imdb_id (Optional[int]): TMDB id of the movie to add
            tmdb_id (Optional[int]): TMDB id of the movie to add
            movie_info (Optional[RadarrMovieItem]): Description of the movie to add
            monitored (bool): Whether to monitor the movie. Default is True
            search (bool): Whether to search for the movie once added. Default is True
        Returns:
            json response
        """
        # Get info from imdb/tmdb if needed:
        if tmdb_id or imdb_id:
            movie_info = self.lookup_movie(tvdb_id=tmdb_id, imdb_id=imdb_id)

        # Prepare movie info for adding
        root_path = self.get_root_folder()
        movie_info.path = root_path["path"] + movie_info.title
        movie_info.profileId = quality
        movie_info.qualityProfileId = quality
        movie_info.monitored = monitored
        movie_info.add_attribute("addOptions", {"searchForMovie": search})

        return self.add_item(json_data=movie_info.to_dict())

    def delete_movie(self, movie_id: int, delete_files: bool = True, add_exclusion: bool = False):
        """Delete the movie with the given ID

        Args:
            item_id (int):  Item to delete
            delete_files (bool): Optional. Also delete files. Default is True
            add_exclusion: Optionally exclude the movie from further imdb/tvdb auto add
        Returns:
            json response
        """
        options = {"addExclusion": add_exclusion} if add_exclusion else {}
        return self.delete_item(movie_id, delete_files, options)

    def refresh_movie(self, movie_id: Optional[int]):
        """Refresh movie information  and rescan disk.

        Args:
            movie_id (Optional[int]): Movie to refresh, if not set all movies will be refreshed and scanned
        Returns:
            json response
        """
        data = {"name": "RefreshMovie"}
        if movie_id:
            data["movieId"] = movie_id
        return self._sendCommand(data)

    def rescan_movie(self, movie_id: Optional[int]):
        """Scan disk for any downloaded movie for all or specified movie.

        Args:
            movie_id (Optional[int]): Movie to refresh, if not set all movies will be refreshed and scanned
        Returns:
            json response
        """
        data = {"name": "RescanMovie"}
        if movie_id:
            data["movieId"] = movie_id
        return self._sendCommand(data)
