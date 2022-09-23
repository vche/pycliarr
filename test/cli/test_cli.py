import pytest
import sys

from pycliarr.cli import cli
from pycliarr.cli.cli_cmd import select_profile, select_language_profile
from pycliarr.api import radarr, sonarr
from pycliarr.api.exceptions import CliArrError
from unittest.mock import Mock, patch, call


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
        "delete-queue",
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


def test_cli_radarr_blocklist_all(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "blocklist",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_blocklist", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(page=1, sort_key="date", page_size=20, sort_dir="descending")
    mock_exit.assert_called_with(0)


def test_cli_radarr_blocklist(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "blocklist",
        "--page-size", "10",
        "--sort-key", "time",
        "--page", "2",
        "--sort-dir", "descending",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_blocklist", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(page=2, sort_key="time", page_size=10, sort_dir="descending")
    mock_exit.assert_called_with(0)


def test_cli_radarr_deleteblocklist(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "delete-blocklist",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.delete_blocklist", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_notification_all(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "notification",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_notification", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(None)
    mock_exit.assert_called_with(0)


def test_cli_radarr_notification(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "notification",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_notification", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_deletenotification(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "delete-notification",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.delete_notification", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_putnotification(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "put-notification",
        "-i", "1234",
        "-j", '{"key": "value"}',
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.put_notification", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234, {'key': 'value'})
    mock_exit.assert_called_with(0)


def test_cli_radarr_putnotificationfile(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "put-notification",
        "-i", "1234",
        "-f", 'test/data.json',
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.put_notification", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234, {'key': 'value'})
    mock_exit.assert_called_with(0)


def test_cli_radarr_tagdetail(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "tag-detail",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_tag_detail", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_tagetail_all(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "tag-detail",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_tag_detail", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(None)
    mock_exit.assert_called_with(0)


def test_cli_radarr_tag(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "tag",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_tag", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_tag_all(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "tag",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_tag", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(None)
    mock_exit.assert_called_with(0)


def test_cli_radarr_deletetag(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "delete-tag",
        "-i", "1234",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.delete_tag", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_edittag(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "edit-tag",
        "-i", "1234",
        "-l", "value",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.edit_tag", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234, 'value')
    mock_exit.assert_called_with(0)


def test_cli_radarr_createttag(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "create-tag",
        "value",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.create_tag", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with('value')
    mock_exit.assert_called_with(0)


def test_cli_radarr_root_folders(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "root-folders",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value = [{'id':1, 'path': '/a/b/c', 'freeSpace': 23000000}])

    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_root_folder", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_sonarr_tagitems_serie(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "tag-items",
        "-l", "value",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value=[
        {"id": 1234, "label": "value", "seriesIds": [1, 2, 3]},
        {"id": 456, "label": "value2", "seriesIds": [4, 5, 6]}
    ])
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_tag_detail", mock_sonarr)
    mock_sonarr2 = Mock(return_value=sonarr.SonarrSerieItem())
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_serie", mock_sonarr2)
    cli.main()
    mock_sonarr2.assert_has_calls([call(1), call(2), call(3)])
    mock_exit.assert_called_with(0)


def test_cli_sonarr_tagitems_id(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "tag-items",
        "-i", "456",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value={"id": 456, "label": "value2", "seriesIds": [4, 5, 6]})
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_tag_detail", mock_sonarr)
    mock_sonarr2 = Mock(return_value=sonarr.SonarrSerieItem())
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_serie", mock_sonarr2)
    cli.main()
    mock_sonarr2.assert_has_calls([call(4), call(5), call(6)])
    mock_exit.assert_called_with(0)


def test_cli_sonarr_tagitems_badval(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "tag-items",
        "-i", "456",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value={"id": 456, "label": "value2"})
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_tag_detail", mock_sonarr)
    mock_sonarr2 = Mock(return_value=sonarr.SonarrSerieItem())
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_serie", mock_sonarr2)
    cli.main()
    mock_exit.assert_called_with(0)


def test_cli_sonarr_tagitems_badtag(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "tag-items",
        "-l", "something",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value=[{"id": 456, "label": "value2"}])
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_tag_detail", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(0)


def test_cli_radarr_tagitems_serie(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "tag-items",
        "-l", "value",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value=[{"id": 1234, "label": "value", "movieIds": [1, 2, 3]}])
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_tag_detail", mock_sonarr)
    mock_sonarr2 = Mock(return_value=radarr.RadarrMovieItem())
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_movie", mock_sonarr2)
    cli.main()
    mock_sonarr2.assert_has_calls([call(1), call(2), call(3)])
    mock_exit.assert_called_with(0)


def test_cli_sonarr_get_exclusion(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "exclusion",
        "-i", "12345",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value={"id": 12345})
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_exclusion", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(0)


def test_cli_sonarr_get_exclusion_all(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "exclusion",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value=[{"id": 12345}, {"id": 2233}])
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_exclusion", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(0)


def test_cli_sonarr_delete_exclusion(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "delete-exclusion",
        "-i", "12345",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value={"id": 12345})
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.delete_exclusion", mock_sonarr)
    cli.main()
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
        "-j",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value = [radarr.RadarrMovieItem(), radarr.RadarrMovieItem()])
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
    mock_sonarr = Mock(return_value = radarr.RadarrMovieItem())
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_radarr_get_json(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "get",
        "-i", "1234",
        "-j",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value = radarr.RadarrMovieItem())
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
    mock_sonarr.assert_called_with(1234, delete_files=False, add_exclusion=False)
    mock_exit.assert_called_with(0)


def test_cli_radarr_edit(monkeypatch, mock_exit):
    item_json = radarr.RadarrMovieItem().to_json()
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "edit",
        "-j", item_json,
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value = item_json)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.edit_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_radarr_edit_file(monkeypatch, mock_exit):
    item_json = radarr.RadarrMovieItem().to_json()
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "edit",
        "-f", "test/movie_item.json",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value = item_json)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.edit_movie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
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
    mock_sonarr.assert_called_with(quality=1, tmdb_id=None, imdb_id='tt1234', movie_info=None, path=None, root_id=0)
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
        "--path", "some/path",
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
        'items': [
            {'quality': {'name': 'item1'}, 'allowed': True},
            {'quality': {'name': 'item2'}, 'allowed': False},
            {'id': '2', 'allowed': True},
            {
                'name': 'name2',
                'id': '2',
                'allowed': True,
                'items': [{'quality': {'name': 'item2'}, 'allowed': True}]
            },
        ]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.lookup_movie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_lookup.assert_called_with(term="some movie")
    mock_sonarr.assert_called_with(
        quality=1,
        tmdb_id=None,
        imdb_id=None,
        movie_info=mock_info,
        path="some/path",
        root_id=0
    )
    mock_exit.assert_called_with(0)


@patch('builtins.input', return_value="1")
def test_cli_radarr_add_one_result(mock_input, monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "-t", "some movie",
        "-r", "123"
        # "-q", 1
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    mock_lookup = Mock()
    mock_info = radarr.RadarrMovieItem(title="test1", year=2020)
    mock_lookup.return_value = mock_info
    mock_profiles = Mock()
    mock_profiles.return_value = [{
        'name': 'name',
        'id': '1',
        'items': [
            {'quality': {'name': 'item1'}, 'allowed': True},
            {'quality': {'name': 'item2'}, 'allowed': False},
            {'id': '2', 'allowed': True},
            {
                'name': 'name2',
                'id': '2',
                'allowed': True,
                'items': [{'quality': {'name': 'item2'}, 'allowed': True}]
            },
        ]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_language_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.lookup_movie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_lookup.assert_called_with(term="some movie")
    mock_sonarr.assert_called_with(quality=1, tmdb_id=None, imdb_id=None, movie_info=mock_info, path=None, root_id=123)
    mock_exit.assert_called_with(0)

def test_cli_radarr_add_bad_root(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "--imdb", "tt1234",
        "-q", "1",
        "-r", "/test",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    mock_root_items = Mock(return_value = [{'id':1, 'path': '/a/b/c', 'freeSpace': 230000000000}])
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_root_folder", mock_root_items)
    cli.main()
    mock_exit.assert_called_with(1)


def test_cli_radarr_add_root_path(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "--imdb", "tt1234",
        "-q", "1",
        "-r", '/a/b/c',
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    mock_root_items = Mock(return_value = [{'id':13, 'path': '/a/b/c', 'freeSpace': 230000000000}])
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_root_folder", mock_root_items)
    cli.main()
    mock_sonarr.assert_called_with(quality=1, tmdb_id=None, imdb_id="tt1234", movie_info=None, path=None, root_id=13)
    mock_exit.assert_called_with(0)


@patch('builtins.input', return_value="123")
def test_cli_radarr_add_root_manual(mock_input, monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "--imdb", "tt1234",
        "-q", "1",
        "-r", 'auto',
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    mock_root_items = Mock(return_value = [{'id':13, 'path': '/a/b/c', 'freeSpace': 230000000000}])
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_root_folder", mock_root_items)
    cli.main()
    mock_sonarr.assert_called_with(quality=1, tmdb_id=None, imdb_id="tt1234", movie_info=None, path=None, root_id=123)
    mock_exit.assert_called_with(0)


@patch('builtins.input', return_value="123c")
def test_cli_radarr_add_root_manual_nok(mock_input, monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "--imdb", "tt1234",
        "-q", "1",
        "-r", 'auto',
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    mock_root_items = Mock(return_value = [{'id':13, 'path': '/a/b/c', 'freeSpace': 230000000000}])
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_root_folder", mock_root_items)
    cli.main()
    mock_exit.assert_called_with(2)

@patch('builtins.input', return_value="1c")
def test_select_profile_nok(mock_input):
    mock_cli = Mock()
    mock_cli.get_quality_profiles.return_value = [{
        'name': 'name',
        'id': '13',
        'items': [
            {'quality': {'name': 'item1'}, 'allowed': 'true'},
            {'quality': {'name': 'item2'}, 'allowed': 'false'},
            {
                'name': 'name2',
                'id': '2',
                'allowed': 'true',
                'items': [{'quality': {'name': 'item2'}, 'allowed': 'true'}]
            },
        ]
    }]
    with pytest.raises(Exception):
        select_profile(mock_cli)


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
        'items': [
            {'quality': {'name': 'item1'}, 'allowed': True},
            {'quality': {'name': 'item2'}, 'allowed': False},
            {
                'name': 'name2',
                'id': '2',
                'allowed': 'true',
                'items': [{'quality': {'name': 'item2'}, 'allowed': 'true'}]
            },
        ]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_language_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.lookup_movie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(2)


@patch('builtins.input', return_value="2b")
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
        'items': [{'quality': {'name': 'item1'}, 'allowed': True}]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_language_profiles", mock_profiles)
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
    mock_lookup.return_value = []
    mock_profiles = Mock()
    mock_profiles.return_value = [{
        'name': 'name',
        'id': '1',
        'items': [{'quality': {'name': 'item1'}, 'allowed': True}]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_language_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.lookup_movie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(2)


@patch('builtins.input', return_value="1")
def test_cli_radarr_add_root(mock_input, monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "add",
        "-t", "some movie",
        "--path", "some/path",
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
        'items': [
            {'quality': {'name': 'item1'}, 'allowed': True},
            {'quality': {'name': 'item2'}, 'allowed': False},
            {'id': '2', 'allowed': True},
            {
                'name': 'name2',
                'id': '2',
                'allowed': True,
                'items': [{'quality': {'name': 'item2'}, 'allowed': True}]
            },
        ]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.lookup_movie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.add_movie", mock_sonarr)
    cli.main()
    mock_lookup.assert_called_with(term="some movie")
    mock_sonarr.assert_called_with(
        quality=1,
        tmdb_id=None,
        imdb_id=None,
        movie_info=mock_info,
        path="some/path",
        root_id=0
    )
    mock_exit.assert_called_with(0)


def test_cli_radarr_search_missing(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "search-missing",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.missing_movies_search", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_radarr_create_exclusion(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "radarr",
        "create-exclusion",
        "-t", "a title",
        "-i", "12345"
        "-y", "2020"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value={"id": 12345})
    monkeypatch.setattr("pycliarr.cli.cli_cmd.radarr.RadarrCli.create_exclusion", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(0)


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
        "-j",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value=[sonarr.SonarrSerieItem(), sonarr.SonarrSerieItem()])
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
    mock_sonarr = Mock(return_value=sonarr.SonarrSerieItem())
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(1234)
    mock_exit.assert_called_with(0)


def test_cli_sonarr_get_json(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "get",
        "-i", "1234",
        "-j",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value=sonarr.SonarrSerieItem())
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
    mock_sonarr.assert_called_with(1234, delete_files=False, add_exclusion=False)
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


def test_cli_sonarr_add_tvdb(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "add",
        "--tvdb", "1234",
        "-q", "1",
        "-l", "1",
        "--season-folders",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.add_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(
        quality=1,
        tvdb_id=1234,
        serie_info=None,
        monitored_seasons=[],
        season_folder=True,
        path=None,
        root_id=0,
        language=1,
    )
    mock_exit.assert_called_with(0)


def test_cli_sonarr_add_tvdb_with_seasons(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "add",
        "--tvdb", "1234",
        "-q", "1",
        "-l", "1",
        "-s", "1, 3",
        "--path", "some/path"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.add_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called_with(
        quality=1,
        tvdb_id=1234,
        serie_info=None,
        monitored_seasons=[1, 3],
        season_folder=False,
        path="some/path",
        root_id=0,
        language=1
    )
    mock_exit.assert_called_with(0)


def test_cli_sonarr_add_tvdb_with_invalidseasons(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "add",
        "--tvdb", "1234",
        "-q", "1",
        "-l", "1",
        "-s", "1, x"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.add_serie", mock_sonarr)
    cli.main()
    mock_sonarr.assert_not_called
    mock_exit.assert_called_with(2)


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
        'items': [{'quality': {'name': 'item1'}, 'allowed': True}]
    }]
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_quality_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_language_profiles", mock_profiles)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.lookup_serie", mock_lookup)
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.add_serie", mock_sonarr)
    cli.main()
    mock_lookup.assert_called_with(term="some serie")
    mock_sonarr.assert_called_with(
        quality=1,
        tvdb_id=None,
        serie_info=mock_info,
        monitored_seasons=[],
        season_folder=False,
        path=None,
        root_id=0,
        language=1,
    )
    mock_exit.assert_called_with(0)


@patch('builtins.input', return_value="1c")
def test_select_language_nok(mock_input):
    mock_cli = Mock()
    mock_cli.get_language_profiles.return_value = [{
        'name': 'name',
        'id': '1',
        'items': [{'quality': {'name': 'item1'}, 'allowed': True}]
    }]
    with pytest.raises(Exception):
        select_language_profile(mock_cli)


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


def test_cli_sonarr_deleteepisode(monkeypatch, mock_exit):
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


def test_cli_sonarr_search_missing(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "search-missing",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock()
    mock_sonarr.return_value = TEST_JSON
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.missing_episodes_search", mock_sonarr)
    cli.main()
    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)


def test_cli_sonarr_create_exclusion(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "create-exclusion",
        "-t", "a title",
        "-i", "12345"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value={"id": 12345})
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.create_exclusion", mock_sonarr)
    cli.main()
    mock_exit.assert_called_with(0)


def test_cli_sonarr_root_folders(monkeypatch, mock_exit):
    test_args = [
        "pycliarr",
        "-t", TEST_HOST,
        "-k", TEST_APIKEY,
        "sonarr",
        "root-folders",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    mock_sonarr = Mock(return_value = [{'id':1, 'path': '/a/b/c', 'freeSpace': 23000000000000000000000000}])
    monkeypatch.setattr("pycliarr.cli.cli_cmd.sonarr.SonarrCli.get_root_folder", mock_sonarr)
    cli.main()

    mock_sonarr.assert_called()
    mock_exit.assert_called_with(0)
