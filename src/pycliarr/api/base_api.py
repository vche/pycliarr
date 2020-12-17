import json
import logging
from pprint import pformat
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import requests

from pycliarr.api.exceptions import CliArrError, CliDecodeError, CliServerError

log = logging.getLogger(__name__)
json_dict = Dict[str, Any]
json_list = List[json_dict]
json_data = Union[json_dict, json_list]
BaseItemClass = TypeVar("BaseItemClass", bound="BaseCliApiItem")


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
        url_params: Optional[Dict[str, Any]] = None,
        json_data: Optional[json_data] = None,
    ) -> json_data:
        """Send a request to the host API

        Args:
            method:
            path (str): host endpoint path. Must start with a '/'. e.g. /api/queue
            url_params (Optional[Dict[str, Any]]): Optional list of query parameters. e.g. {'term': 'some keyword'}
            json_data (Optional[json_data]): Optional JSON data to send
        Returns:
            requests.models.Response: Response object form requests.
        """
        request_url = f"{self.host_url}{path}"
        log.debug("Request sent: %s %s params: %s data: %s", method, request_url, url_params, json_data)
        try:
            res = self._session.request(method, request_url, params=url_params, json=json_data)
            # log.debug(f"Result {res.status_code}, Body {res.content}")
        except Exception as e:
            raise CliArrError(f"Error sending request {request_url}: {e}")
        if res.status_code >= 400:
            raise CliServerError(
                f"Error from server {request_url}, status: {res.status_code}, msg: {pformat(res.content.decode())}",
                status_code=res.status_code,
            )
        try:
            body: Dict[str, Any] = res.json()
            return body
        except Exception as e:
            raise CliDecodeError(f"Error parsing response {res.content.decode()} from {request_url}: {e}")

    def request_get(self, path: str, url_params: Optional[Dict[str, Any]] = None) -> json_data:
        """Shortcut for request withe method=get."""
        return self.request("GET", path, url_params=url_params)

    def request_post(self, path: str, json_data: Optional[json_data] = None) -> json_data:
        """Shortcut for request withe method=post."""
        return self.request("POST", path, json_data=json_data)

    def request_put(self, path: str, json_data: Optional[json_data] = None) -> json_data:
        """Shortcut for request withe method=put."""
        return self.request("PUT", path, json_data=json_data)

    def request_delete(self, path: str, json_data: Optional[json_data] = None) -> json_data:
        """Shortcut for request withe method=delete."""
        return self.request("DELETE", path, json_data=json_data)

    def close(self) -> None:
        """Close session with the endpoint."""
        self._session.close()


class BaseCliApiItem:
    """Generic handling of an item based on a dict representation.

    Items can be build specifying a list of parameters, a dict, or a json string.
    All fields are directly accessible as attributes.

    This is especially usedul by clients to directly convert or create items received or to send
    by BaseCliApi subclasses
    """

    def __init__(self, **kwargs: Any) -> None:
        """Build an item and populate it with the keys specified."""
        self._data = self._model()
        self._update_existing(kwargs)

    @classmethod
    def from_dict(cls: Type[BaseItemClass], dict_data: Dict[Any, Any]) -> BaseItemClass:
        """Build an item and populate it based on the given dictionnary."""
        new_obj: BaseItemClass = cls()
        new_obj._update_existing(dict_data)
        return new_obj

    @classmethod
    def from_json(cls: Type[BaseItemClass], json_data: str) -> BaseItemClass:
        """Build an item and populate it based on json data."""
        return cls.from_dict(json.loads(json_data))

    def _update_existing(self, dict_data: Dict[Any, Any]) -> None:
        """Update a dict only if the keys already exist."""
        for key in dict_data:
            if key in self._data:
                self._data[key] = dict_data[key]

    def _model(self) -> Dict[Any, Any]:
        """Define the model of items represented by this class.

        Should be overwritten by all children
        """
        return {
            # Accepted keys and default values must be defined here by subclasses
            "test": ""
        }

    def to_dict(self) -> Dict[Any, Any]:
        return self._data

    def add_attribute(self, name: str, value: Any) -> None:
        self._data[name] = value

    def __repr__(self) -> str:
        return str(pformat(self.to_dict(), indent=2))

    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        else:
            raise AttributeError(f"{self.__class__.__name__} object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> Any:
        if "_data" in self.__dict__ and name in self._data:
            self.__dict__["_data"][name] = value
        else:
            super().__setattr__(name, value)  # pragma: no cover
