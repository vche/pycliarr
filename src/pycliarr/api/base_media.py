import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from pycliarr.api.base_api import BaseCliApi, json_data, json_dict, json_list
from pycliarr.api.exceptions import CliArrError

log = logging.getLogger(__name__)


class BaseCliMediaApi(BaseCliApi):
    """Base class for media based API.

    Implement behavior common to media based apis (e.g. sonarr, radarr)
    """

    # Default urls for commands. Some might need to be overriden by the childs.
    api_url_base = "/api/v3"
    api_url_calendar = f"{api_url_base}/calendar"
    api_url_command = f"{api_url_base}/command"
    api_url_diskspace = f"{api_url_base}/diskspace"
    api_url_item = f"{api_url_base}/item"
    api_url_itemlookup = f"{api_url_base}/item/lookup"
    api_url_systemstatus = f"{api_url_base}/system/status"
    api_url_queue = f"{api_url_base}/queue"
    api_url_history = f"{api_url_base}/history/"
    api_url_profile = f"{api_url_base}/qualityProfile"
    api_url_rootfolder = f"{api_url_base}/rootfolder"
    api_url_log = f"{api_url_base}/log"
    api_url_systembackup = f"{api_url_base}/system/backup"
    api_url_wanted_missing = f"{api_url_base}/wanted/missing"
    api_url_blocklist = f"{api_url_base}/blocklist"
    api_url_notification = f"{api_url_base}/notification"
    api_url_tag = f"{api_url_base}/tag"
    api_url_exclusions = f"{api_url_base}/importlistexclusion"
    api_url_rename = f"{api_url_base}/rename"

    def __init__(self, *args: Any, default_root_folder_id: int = 0, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._default_root_folder_id = default_root_folder_id

    @property
    def default_root_folder_id(self) -> int:
        return self._default_root_folder_id

    @default_root_folder_id.setter
    def default_root_folder_id(self, value: int) -> None:
        self._default_root_folder_id = value

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

    def get_disk_space(self) -> json_data:
        """Retrieve info about the disk space on the server.

        Returns:
            json response
        """
        return self.request_get(self.api_url_diskspace)

    def get_root_folder(self) -> List[json_dict]:
        """Retrieve the server root folder.

        Returns:
            json response
        """
        res = cast(json_list, self.request_get(self.api_url_rootfolder))
        return res

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
        """Adds a new item to collection

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

    def edit_item(self, json_data: json_data, url_params: Optional[Dict[str, Any]] = None) -> json_data:
        """Edit an item from the collection

        Args:
            json_data: Dict representation of the item to add
        Returns:
            json response
        """
        return self.request_put(self.api_url_item, json_data=json_data, url_params=url_params)

    def get_system_status(self) -> json_data:
        """Return the System Status as json"""
        return self.request_get(self.api_url_systemstatus)

    def get_quality_profiles(self) -> json_list:
        """Return the quality profiles"""
        return cast(json_list, self.request_get(self.api_url_profile))

    def _get_queue(
        self,
        page: int = 1,
        sort_key: str = "progress",
        page_size: int = 20,
        sort_dir: str = "ascending",
        options: Dict[str, Any] = {},
    ) -> json_data:
        """Get queue info (downloading/completed, ok/warning) as json

        Args:
            page (int) - 1-indexed (1 default)
            sort_key (string) - title or date
            page_size (int) - Default: 10
            sort_dir (string) - asc or desc - Default: asc
            options (Dict[str, Any]={}): Optional additional options
        """
        data = {
            "page": page,
            "pageSize": page_size,
            "sortKey": sort_key,
            "sortDirection": sort_dir,
        }
        data.update(options)
        return self.request_get(self.api_url_queue, url_params=data)

    def get_queue(
        self,
        page: int = 1,
        sort_key: str = "progress",
        page_size: int = 20,
        sort_dir: str = "ascending",
        include_unknown: bool = True,
    ) -> json_data:
        return self._get_queue(page, sort_key, page_size, sort_dir)

    def delete_queue(self, item_id: int, blacklist: Optional[bool] = None) -> json_data:
        """Delete an item from the queue and download client. Optionally blacklist item after deletion.

        Args:
            item_id (int):  Item to delete
            blacklist (Optional[bool]): Optionally blacklist the item
        Returns:
            json response
        """
        data = {}
        if blacklist:
            data["blacklist"] = blacklist
        return self.request_delete(f"{self.api_url_queue}/{item_id}", data)

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

    def build_item_path(self, title: str, root_folder_id: int = 0) -> Path:
        """Build an item folder path using the root folder specified.
        Args:
            title (str): Title to add to root path. All invalid characters are removed
            root_folder_id (int): Id of the root folder (can be retrieved with get_root_folder()).
            If the id is not found or not specified, the default root folder id will be used.
            If 0, the first root folder in the list is used.

        Returns: Full path of the serie in the format <root path>/<serie name>
        """
        root_paths = self.get_root_folder()
        selected_root_folder_id = root_folder_id or self.default_root_folder_id
        print(f"{selected_root_folder_id} // {root_folder_id} // {self.default_root_folder_id}")
        root_path = root_paths[0] if not selected_root_folder_id else None
        for path in root_paths:
            if path["id"] == int(selected_root_folder_id):
                root_path = path

        if not root_path:
            raise CliArrError(f"Invalid root folder Id: {selected_root_folder_id}")
        return Path(root_path["path"]) / self.to_path(title)

    def get_blocklist(
        self, page: int = 1, sort_key: str = "date", page_size: int = 20, sort_dir: str = "descending"
    ) -> json_data:
        """Get blocklisted releases

        Args:
            page (int) - 1-indexed (1 default)
            sort_key (string) - date
            page_size (int) - Default: 20
            sort_dir (string) - ascending or descending - Default: descending
        """
        data = {
            "page": page,
            "pageSize": page_size,
            "sortKey": sort_key,
            "sortDirection": sort_dir,
        }
        return self.request_get(self.api_url_blocklist, url_params=data)

    def delete_blocklist(self, item_id: Optional[int] = None) -> json_data:
        """Remove the specified item from the blocklist, or all items if none specified

        Args:
            item_id (int):  Item to delete, None to delete all items
        Returns:
            json response
        """
        if item_id:
            return self.request_delete(self.api_url_blocklist, url_params={"id": item_id})
        else:
            return self.request_delete(f"{self.api_url_blocklist}/bulk")

    def get_notification(self, item_id: Optional[int] = None) -> json_data:
        """Get specified notification or all if none specified

        Args:
            item_id (int):  id of the notification to get, or None to get all of them
        Returns:
            json response
        """
        return self.request_get(f"{self.api_url_notification}/{item_id if item_id else ''}")

    def delete_notification(self, item_id: int) -> json_data:
        """Remove the specified item from the blocklist, or all items if none specified

        Args:
            item_id (int):  id of the notification to delete
        Returns:
            json response
        """
        return self.request_delete(f"{self.api_url_notification}/{item_id}")

    def put_notification(self, item_id: int, notification_data: json_data) -> json_data:
        """Create the specified notification

        Args:
            item_id (int):  id of the notification to create
            notification_data (json_data): Json dict describing the notification formated as in
                https://radarr.video/docs/api/#/Notification/put-notification-id
        Returns:
            json response
        """
        return self.request_put(f"{self.api_url_notification}/{item_id}", json_data=notification_data)

    def get_tag(self, item_id: Optional[int] = None) -> json_data:
        """Get specified tag or all if none specified

        Args:
            item_id (int):  id of the tag to get, or None to get all of them
        Returns:
            json response
        """
        return self.request_get(f"{self.api_url_tag}/{item_id if item_id else ''}")

    def get_tag_detail(self, item_id: Optional[int] = None) -> json_data:
        """Get specified tag detail or all if none specified

        Args:
            item_id (int):  id of the tag to get, or None to get all of them
        Returns:
            json response
        """
        return self.request_get(f"{self.api_url_tag}/detail/{item_id if item_id else ''}")

    def delete_tag(self, item_id: int) -> json_data:
        """Remove the specified tag

        Args:
            item_id (int):  id of the notification to delete
        Returns:
            json response
        """
        return self.request_delete(f"{self.api_url_tag}/{item_id}")

    def edit_tag(self, item_id: int, value: str) -> json_data:
        """Edit the specified tag

        Args:
            item_id (int):  id of the tag to edit
            value (str): Tag label
        Returns:
            json response
        """
        return self.request_put(f"{self.api_url_tag}/{item_id}", json_data={"id": item_id, "label": value})

    def create_tag(self, value: str) -> json_data:
        """Create the specified tag

        Args:
            item_id (int):  id of the tag to edit
            value (str): Tag label
        Returns:
            json response
        """
        return self.request_post(self.api_url_tag, json_data={"id": 0, "label": value})

    def get_exclusion(self, item_id: Optional[int] = None) -> json_data:
        """Get import list exclusions

        Args:
            item_id (int):  id of the exclusion to get, or None to get all of them
        Returns:
            json response
        """
        return self.request_get(f"{self.api_url_exclusions}/{item_id if item_id else ''}")

    def delete_exclusion(self, item_id: int) -> json_data:
        """Remove the specified exclusions

        Args:
            item_id (int):  id of the exclusions to delete
        Returns:
            json response
        """
        return self.request_delete(f"{self.api_url_exclusions}/{item_id}")
