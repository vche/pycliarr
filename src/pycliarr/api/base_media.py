import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from pycliarr.api.base_api import BaseCliApi, json_data, json_dict, json_list

log = logging.getLogger(__name__)


class BaseCliMediaApi(BaseCliApi):
    """Base class for media based API.

    Implement behavior common to media based apis (e.g. sonarr, radarr)
    """

    # Default urls for commands. Some might need to be overriden by the childs.
    api_url_base = "/api/"
    api_url_calendar = f"{api_url_base}/calendar"
    api_url_command = f"{api_url_base}/command"
    api_url_diskspace = f"{api_url_base}/diskspace"
    api_url_item = f"{api_url_base}/item"
    api_url_itemlookup = f"{api_url_base}/item/lookup"
    api_url_systemstatus = f"{api_url_base}/system/status"
    api_url_queue = f"{api_url_base}/queue"
    api_url_history = f"{api_url_base}/history/"
    api_url_profile = f"{api_url_base}/profile"
    api_url_rootfolder = f"{api_url_base}/rootfolder"
    api_url_log = f"{api_url_base}/log"
    api_url_systembackup = f"{api_url_base}/system/backup"
    api_url_wanted_missing = f"{api_url_base}/wanted/missing"

    def get_calendar(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> json_data:
        """Retrieve info about when items were/will be downloaded.

        If start and end are not provided, retrieves movies airing today and tomorrow.
        Args:
            start_date (Optional[datetime]):  Start date of events to retrieve
            end_date (Optional[datetime]):    End date of events to retrieve
        Returns:
            json response
        """
        url_params = {}
        if start_date and end_date:
            url_params["start"] = start_date.strftime("%Y-%m-%d")
            url_params["end"] = end_date.strftime("%Y-%m-%d")
        return self.request_get(self.api_url_calendar, url_params=url_params)

    def get_command(self, cid: Optional[int] = None) -> json_data:
        """Query the status of a previously started command, or all currently running.

        Args:
            cid (Optional[int]) Unique ID of command
        Returns:
            json response
        """
        url_path = f"{self.api_url_command}/{cid}" if cid else self.api_url_command
        return self.request_get(url_path)

    def _sendCommand(self, data: json_data) -> json_data:
        return self.request_post(self.api_url_command, json_data=data)

    def sync_rss(self) -> json_data:
        """Perform an RSS sync with all enabled indexers.

        Returns:
            json response
        """
        return self._sendCommand({"name": "RssSync"})

    def rename_files(self, file_ids: List[int]) -> json_data:
        """Rename the list of files provided.

        Args:
            file_ids (List[int]): List of ids of files to rename
        Returns:
            json response
        """
        return self._sendCommand({"name": "RenameFiles", "files": file_ids})

    def get_disk_space(self) -> json_data:
        """Retrieve info about the disk space on the server.

        Returns:
            json response
        """
        return self.request_get(self.api_url_diskspace)

    def get_root_folder(self) -> json_dict:
        """Retrieve the server root folder.

        Returns:
            json response
        """
        res = cast(json_list, self.request_get(self.api_url_rootfolder))
        return res[0]

    def get_item(self, item_id: Optional[int] = None) -> json_data:
        """Get specified item, or all if no id provided from server collection.

        Args:
            item_id (Optional[int]) ID of item to get, all items by default
        Returns:
            json response
        """
        url_path = f"{self.api_url_item}/{item_id}" if item_id else self.api_url_item
        return self.request_get(url_path)

    def lookup_item(self, term: str) -> json_data:
        """Search for items

        Args:
            term (str): Lookup terms
        Returns:
            json response
        """
        url_params = {"term": term}
        return self.request_get(self.api_url_itemlookup, url_params=url_params)

    def add_item(self, json_data: json_data) -> json_data:
        """addMovie adds a new movie to collection

        Args:
            json_data: Dict representation of the item to add
        Returns:
            json response
        """
        return self.request_post(self.api_url_item, json_data=json_data)

    def delete_item(self, item_id: int, delete_files: bool = True, options: Dict[str, Any] = {}) -> json_data:
        """Delete the item with the given ID

        Args:
            item_id (int):  Item to delete
            delete_files (bool): Optional. Also delete files. Default is False
            options (Dict[str, Any]): Optionally specify additional options
        Returns:
            json response
        """
        data = {"deleteFiles": delete_files}
        data.update(options)
        url_path = f"{self.api_url_item}/{item_id}"
        return self.request_delete(url_path, data)

    def get_system_status(self) -> json_data:
        """Return the System Status as json"""
        return self.request_get(self.api_url_systemstatus)

    def get_quality_profiles(self) -> json_list:
        """Return the quality profiles"""
        return cast(json_list, self.request_get(self.api_url_profile))

    def get_queue(self) -> json_data:
        """Get queue info (downloading/completed, ok/warning) as json"""
        return self.request_get(self.api_url_queue)

    def delete_queue(self, item_id: int, blacklist: Optional[bool] = None) -> json_data:
        """Delete an item from the queue and download client. Optionally blacklist item after deletion.

        Args:
            item_id (int):  Item to delete
            blacklist (Optional[bool]): Optionally blacklist the item
        Returns:
            json response
        """
        data = {"id": item_id}
        if blacklist:
            data["blacklist"] = blacklist
        return self.request_delete(self.api_url_queue, data)

    def get_history(
        self,
        page: int = 1,
        sort_key: str = "date",
        page_size: int = 10,
        sort_dir: str = "asc",
        options: Dict[str, Any] = {},
    ) -> json_data:
        """Get history (grabs/failures/completed)

        Args:
            page (int) - 1-indexed (1 default)
            sort_key (string) - title or date
            page_size (int) - Default: 10
            sort_dir (string) - asc or desc - Default: asc
            options (Dict[str, Any]={}): Optional additional options
        Returns:
            json response
        """
        data = {
            "page": page,
            "pageSize": page_size,
            "sortKey": sort_key,
            "sortDir": sort_dir,
        }
        data.update(options)
        return self.request_get(self.api_url_history, url_params=data)

    def get_logs(self, page: int = 1, sort_key: str = "time", page_size: int = 10, sort_dir: str = "asc") -> json_data:
        """Get logs

        Args:
            page (int) - 1-indexed (1 default)
            sort_key (string) - title or time
            page_size (int) - Default: 10
            sort_dir (string) - asc or desc - Default: asc
        Returns:
            json response
        """
        data = {
            "page": page,
            "pageSize": page_size,
            "sortKey": sort_key,
            "sortDir": sort_dir,
        }
        return self.request_get(self.api_url_log, url_params=data)

    def get_backup(self) -> json_data:
        """Return the backups as json"""
        return self.request_get(self.api_url_systembackup)

    def get_wanted(
        self, page: int = 1, sort_key: str = "airDateUtc", page_size: int = 10, sort_dir: str = "asc"
    ) -> json_data:
        """Get Wanted / Missing episodes

        Args:
            sort_key (str): series.title or airDateUtc (default)
            page (int): 1-indexed Default: 1
            page_size (int): Default: 10
            sort_dir (str): asc or desc - Default: asc
        Returns:
            json response
        """
        data = {
            "page": page,
            "pageSize": page_size,
            "sortKey": sort_key,
            "sortDir": sort_dir,
        }
        data.update({"sortKey": sort_key})
        return self.request_get(self.api_url_wanted_missing, url_params=data)
