from pycliarr.api.base import BaseCliApi, BaseCliMediaApi
from pycliarr.api.exceptions import CliArrError
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


@patch("pycliarr.api.base.requests.Session")
def test_get_with_auth(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, [TEST_JSON])
    code, rep = cli.get(TEST_PATH, {'param': 'value'})
    cli.close()

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with(
        "GET", f"{TEST_HOST}{TEST_PATH}", params={'param': 'value'}, json=None
    )
    patch_session().close.assert_called()
    assert code == 200
    assert rep == TEST_JSON


@patch("pycliarr.api.base.requests.Session")
def test_request_error(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.side_effect = Exception

    with pytest.raises(CliArrError):
        code, rep = cli.get(TEST_PATH)

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with("GET", f"{TEST_HOST}{TEST_PATH}", params=None, json=None)


@patch("pycliarr.api.base.requests.Session")
def test_response_error(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, Exception)

    with pytest.raises(CliArrError):
        code, rep = cli.get(TEST_PATH)

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with("GET", f"{TEST_HOST}{TEST_PATH}", params=None, json=None)


@patch("pycliarr.api.base.requests.Session")
def test_put(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, [TEST_JSON])
    code, rep = cli.put(TEST_PATH, {'param': 'value'})

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with(
        "PUT", f"{TEST_HOST}{TEST_PATH}", params=None, json={'param': 'value'}
    )
    assert code == 200
    assert rep == TEST_JSON


@patch("pycliarr.api.base.requests.Session")
def test_post(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, [TEST_JSON])
    code, rep = cli.post(TEST_PATH, {'param': 'value'})

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with(
        "POST", f"{TEST_HOST}{TEST_PATH}", params=None, json={'param': 'value'}
    )
    assert code == 200
    assert rep == TEST_JSON


@patch("pycliarr.api.base.requests.Session")
def test_delete(patch_session):
    cli = BaseCliApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, [TEST_JSON])
    code, rep = cli.delete(TEST_PATH, {'param': 'value'})

    assert patch_session().headers == {"X-Api-Key": TEST_APIKEY}
    patch_session().request.assert_called_with(
        "DELETE", f"{TEST_HOST}{TEST_PATH}", params=None, json={'param': 'value'}
    )
    assert code == 200
    assert rep == TEST_JSON


@patch("pycliarr.api.base.requests.Session")
def test_get_with_auth(patch_session):
    cli = BaseCliMediaApi(TEST_HOST, TEST_APIKEY, username=TEST_USER, password=TEST_PASS)
    patch_session().request.return_value = mock_response(200, [TEST_JSON])

    cli.list()
    cli.get_movie("id")
    cli.close()
