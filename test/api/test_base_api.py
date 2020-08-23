from pycliarr.api.base_api import BaseCliApi, BaseCliApiItem
from pycliarr.api.base_media import BaseCliMediaApi
from pycliarr.api.exceptions import CliArrError, CliServerError
from unittest.mock import Mock, patch
import pytest


TEST_HOST = "http://example.com"
TEST_APIKEY = "abcd1234"
TEST_USER = "user"
TEST_PASS = "pass"
TEST_PATH = "/api/test"
TEST_JSON = {'some': 'value'}


def mock_response(code, data_dict):
    resp = Mock()
    resp.status_code = code
    resp.json.side_effect = data_dict
    return resp


@patch("pycliarr.api.base_api.requests.Session")
def test_get_with_auth(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, [TEST_JSON])
    rep = cli.request_get(TEST_PATH, {'param': 'value'})
    cli.close()

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with(
        "GET", f"{TEST_HOST}{TEST_PATH}", params={'param': 'value'}, json=None
    )
    patch_session().close.assert_called()
    assert rep == TEST_JSON


@patch("pycliarr.api.base_api.requests.Session")
def test_request_error(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.side_effect = Exception

    with pytest.raises(CliArrError):
        cli.request_get(TEST_PATH)

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with("GET", f"{TEST_HOST}{TEST_PATH}", params=None, json=None)


@patch("pycliarr.api.base_api.requests.Session")
def test_response_error(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, Exception)

    with pytest.raises(CliArrError):
        cli.request_get(TEST_PATH)

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with("GET", f"{TEST_HOST}{TEST_PATH}", params=None, json=None)


@patch("pycliarr.api.base_api.requests.Session")
def test_server_error(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(400, Exception)

    with pytest.raises(CliServerError):
        cli.request_get(TEST_PATH)

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with("GET", f"{TEST_HOST}{TEST_PATH}", params=None, json=None)


@patch("pycliarr.api.base_api.requests.Session")
def test_put(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, [TEST_JSON])
    rep = cli.request_put(TEST_PATH, {'param': 'value'})

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with(
        "PUT", f"{TEST_HOST}{TEST_PATH}", params=None, json={'param': 'value'}
    )
    assert rep == TEST_JSON


@patch("pycliarr.api.base_api.requests.Session")
def test_post(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, [TEST_JSON])
    rep = cli.request_post(TEST_PATH, {'param': 'value'})

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with(
        "POST", f"{TEST_HOST}{TEST_PATH}", params=None, json={'param': 'value'}
    )
    assert rep == TEST_JSON


@patch("pycliarr.api.base_api.requests.Session")
def test_delete(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, [TEST_JSON])
    rep = cli.request_delete(TEST_PATH, {'param': 'value'})

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with(
        "DELETE", f"{TEST_HOST}{TEST_PATH}", params=None, json={'param': 'value'}
    )
    assert rep == TEST_JSON


def test_base_item():
    item = BaseCliApiItem(test="a")
    item.add_attribute("b", "c")

    assert item.test == "a"
    assert item.b == "c"
    with pytest.raises(AttributeError):
        item.c

    assert item.to_dict() == {"test": "a", "b": "c"}

    item = BaseCliApiItem.from_dict({"test": "a", "f": "g"})
    item.test = "b"
    assert item.to_dict() == {"test": "b"}

    item = BaseCliApiItem.from_json('{"test": "a"}')
    assert item.to_dict() == {"test": "a"}
