import logging
import urllib.parse
from typing import Any, Dict, Optional, Tuple

import requests

from pycliarr.api.exceptions import CliArrError

log = logging.getLogger(__name__)


class BaseCliApi:
    """Low level base API client class.

    Provides basic requests access (put/get/post/delete) to an API, handling api key and basic authentication
    """

    def __init__(
        self, host_url: str, api_key: str, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """Build an api client from host url and api key.

        Args:
            host_url (str): Host url to sonarr. e.g http://192.168.0.5 or http://www.example.com
            api_key (str):  API key for the service. Can usually be found in general settings.
            username (str): Username to use for basic authentication. Both username and password are needed to use auth.
            password (str): Password to use for basic authentication. Both username and password are needed to use auth.
        """
        self._host_url = host_url
        self._api_key = api_key
        self._session = self._build_session(username, password)

    @property
    def host_url(self) -> str:
        return self._host_url

    @property
    def api_key(self) -> str:
        return self._api_key

    def _build_session(self, username: Optional[str], password: Optional[str]) -> requests.Session:
        session = requests.Session()
        session.auth = requests.auth.HTTPBasicAuth(username, password) if username and password else None
        session.headers = self._set_default_header()  # type: ignore
        return session

    def _set_default_header(self) -> Dict[str, str]:
        """Build a default header containing the api key."""
        return {"X-Api-Key": self.api_key}

    def request(
        self,
        method: str,
        path: str,
        url_param: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        """Send a request to the host API

        Args:
            method:
            path (str): host endpoint path. Must start with a '/'. e.g. /api/queue
            url_param (Optional[Dict[str, Any]]): Optional list of query parameters. e.g. {'term': 'some keyword'}
            json_data (Optional[Dict[str, Any]]): Optional JSON data to send
        Returns:
            requests.models.Response: Response object form requests.
        """
        request_url = f"{self.host_url}{path}"
        log.debug("Request sent: %s Data: %s", request_url, json=json_data)
        try:
            res = self._session.request(method, request_url, params=url_param, json=json_data)
        except Exception as e:
            raise CliArrError(f"Error sending request {request_url}: {e}")
        try:
            return res.status_code, res.json()
        except Exception as e:
            raise CliArrError(f"Error parsing response {res.content.decode()} from {request_url}: {e}")

    def get(self, path: str, url_param: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
        """Shortcut for request withe method=get."""
        return self.request("GET", path, url_param=url_param)

    def post(self, path: str, json_data: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
        """Shortcut for request withe method=post."""
        return self.request("POST", path, json_data=json_data)

    def put(self, path: str, json_data: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
        """Shortcut for request withe method=put."""
        return self.request("PUT", path, json_data=json_data)

    def delete(self, path: str, json_data: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
        """Shortcut for request withe method=delete."""
        return self.request("DELETE", path, json_data=json_data)

    def close(self) -> None:
        """Close session with the endpoint."""
        self._session.close()


class BaseCliMediaApi(BaseCliApi):
    """Base class for media based API.

    Implement behavior common to media based apis (e.g. sonarr, radarr)
    """

    def list(self) -> str:
        return "some list"

    def get_movie(self, mid: str) -> Dict[str, Any]:
        code, res = self.get("/api/movie/lookup", url_param={"term": urllib.parse.quote(mid)})
        return res
