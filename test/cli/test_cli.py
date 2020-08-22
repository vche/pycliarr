import pytest
import sys

from pycliarr.cli import cli
from pycliarr.api.exceptions import CliArrError
from unittest.mock import Mock


TEST_HOST = "http://example.com"
TEST_APIKEY = "abcd1234"
TEST_USER = "user"
TEST_PASS = "pass"
TEST_JSON = {'some': 'value'}


@pytest.fixture
def mock_exit(monkeypatch):
    exit = Mock()
    monkeypatch.setattr(sys, "exit", exit)
    return exit


def test_cli_api_error(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "list",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.side_effect = CliArrError
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.list", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(1)


def test_cli_api_exception(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "list",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.side_effect = Exception
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.list", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(2)


def test_cli_sonarr_list(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "-u", TEST_USER,
        "-p", TEST_PASS,
        "sonarr",
        "list",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.list", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_sonarr_get(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "sonarr",
        "get",
        "-i", "12 34",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = 200, TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with('/api/movie/lookup', url_param={'term': "12%2034"})
    mock_exit.assert_called_with(0)
