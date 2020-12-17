import pytest
import sys

from pycliarr.cli import cli
from pycliarr.api.exceptions import CliArrError
from unittest.mock import Mock, patch


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


def test_cli_api(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "get",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.side_effect = CliArrError
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(1)


def test_cli_api_error_debug(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "-d",
        "radarr",
        "get",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.side_effect = CliArrError
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(1)


def test_cli_api_exception(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "get",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.side_effect = Exception
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(2)


def test_cli_api_exception_debug(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "-d",
        "radarr",
        "get",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.side_effect = Exception
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(2)


##############################################
##########  media specific commands ##########
##############################################
def test_cli_radarr_profile(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        '-d',
        "radarr",
        "profiles",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    profiles_json = [{
        'name': 'name',
        'id': 'id',
        'items': [{'quality': {'name': 'item1'}, 'allowed': 'true'}]
    }]
    mock_sonarr.return_value = profiles_json
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_radarr_sysstatus(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "system-status",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_system_status", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_radarr_diskspace(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "disk-space",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_disk_space", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_radarr_queue(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "queue",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_queue", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_radarr_deletequeue(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "delqueue",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.delete_queue", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_calendar(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "calendar",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_calendar", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_radarr_delete(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "delqueue",
        '-i', '1234',
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.delete_queue", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_wanted(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "wanted",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_wanted", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_radarr_status(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "status",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_command", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


##############################################
########## radarr specific commands ##########
##############################################
def test_cli_radarr_list(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "-u", TEST_USER,
        "-p", TEST_PASS,
        "radarr",
        "get",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_radarr_get(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "get",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_delete(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "delete",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.delete_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234, delete_files=False)
    mock_exit.assert_called_with(0)


def test_cli_radarr_rescan(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "rescan",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.rescan_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_refresh(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "refresh",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.refresh_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_add_imdb(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "--imdb", "tt1234",
        "-q", "1",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(quality=1, tmdb_id=None, imdb_id='tt1234', movie_info=None)
    mock_exit.assert_called_with(0)


@patch('builtins.input', return_value="1")
def test_cli_radarr_add_manual(mock_input, monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "-t", "some movie",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    mock_lookup = Mock()
    mock_info = Mock(title="test1", year=2020)
    mock_lookup.return_value = [mock_info]
    mock_profiles = Mock()
    mock_profiles.return_value = [{
        'name': 'name',
        'id': '1',
        'items': [{'quality': {'name': 'item1'}, 'allowed': 'true'}]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.lookup_movie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_lookup.assert_called_with(term="some movie")
    mock_sonarr.assert_called_with(quality=1, tmdb_id=None, imdb_id=None, movie_info=mock_info)
    mock_exit.assert_called_with(0)


@patch('builtins.input', return_value="2")
def test_cli_radarr_add_manual_badmovie(mock_input, monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "-t", "some movie",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    mock_lookup = Mock()
    mock_info = Mock(title="test1", year=2020)
    mock_lookup.return_value = [mock_info]
    mock_profiles = Mock()
    mock_profiles.return_value = [{
        'name': 'name',
        'id': '1',
        'items': [{'quality': {'name': 'item1'}, 'allowed': 'true'}]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.lookup_movie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(2)


@patch('builtins.input', return_value="2")
def test_cli_radarr_add_manual_badprofile(mock_input, monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "-t", "some movie",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    mock_lookup = Mock()
    mock_info = Mock(title="test1", year=2020)
    mock_lookup.return_value = [mock_info, Mock(title="test2", year=2020)]
    mock_profiles = Mock()
    mock_profiles.return_value = [{
        'name': 'name',
        'id': '1',
        'items': [{'quality': {'name': 'item1'}, 'allowed': 'true'}]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.lookup_movie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(2)


@patch('builtins.input', return_value="1")
def test_cli_radarr_add_manual_nomovie(mock_input, monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "-t", "some movie",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    mock_lookup = Mock()
    mock_info = Mock(title="test1", year=2020)
    mock_lookup.return_value = []
    mock_profiles = Mock()
    mock_profiles.return_value = [{
        'name': 'name',
        'id': '1',
        'items': [{'quality': {'name': 'item1'}, 'allowed': 'true'}]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.lookup_movie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(2)


##############################################
########## sonarr specific commands ##########
##############################################
def test_cli_sonarr_list(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "-u", TEST_USER,
        "-p", TEST_PASS,
        "sonarr",
        "get",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_sonarr_get(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "get",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_sonarr_delete(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "delete",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.delete_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234, delete_files=False)
    mock_exit.assert_called_with(0)


def test_cli_sonarr_rescan(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "rescan",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.rescan_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_sonarr_refresh(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "refresh",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.refresh_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_sonarr_add_imdb(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "add",
        "--tvdb", "1234",
        "-q", "1",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.add_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(quality=1, tvdb_id=1234, serie_info=None)
    mock_exit.assert_called_with(0)


@patch('builtins.input', return_value="1")
def test_cli_sonarr_add_manual(mock_input, monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "add",
        "-t", "some serie",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    mock_lookup = Mock()
    mock_info = Mock(title="test1", year=2020)
    mock_lookup.return_value = [mock_info]
    mock_profiles = Mock()
    mock_profiles.return_value = [{
        'name': 'name',
        'id': '1',
        'items': [{'quality': {'name': 'item1'}, 'allowed': 'true'}]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.lookup_serie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.add_serie", mock_sonarr)
    cli.main()
    mock_lookup.assert_called_with(term="some serie")
    mock_sonarr.assert_called_with(quality=1, tvdb_id=None, serie_info=mock_info)
    mock_exit.assert_called_with(0)


def test_cli_sonarr_getepisodefile(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "get-episode-file",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_episode_file", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(serie_id=1234, episode_id=None)
    mock_exit.assert_called_with(0)


def test_cli_sonarr_getepisode(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "get-episode",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_episode", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(serie_id=1234, episode_id=None)
    mock_exit.assert_called_with(0)


def test_cli_sonarr_get(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "delete-episode-file",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.delete_episode_file", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)
