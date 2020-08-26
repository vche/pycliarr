import pytest
from unittest.mock import patch
from pycliarr.api.base_media import BaseCliMediaApi
from datetime import datetime

TEST_JSON = {'somefield': "some value"}
TEST_JSON2 = {'someotherfield': "some other value"}
TEST_HOST = "http://example.com"
TEST_APIKEY = "abcd1234"


@pytest.fixture
def cli():
    return BaseCliMediaApi(TEST_HOST, TEST_APIKEY)


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_calendar(mock_base, cli):
    res = cli.get_calendar()
    mock_base.assert_called_with(cli.api_url_calendar, url_params={})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_calendar_withparams(mock_base, cli):
    start = datetime(year=2020, month=6, day=13)
    end = datetime(year=2020, month=6, day=15)
    res = cli.get_calendar(start_date=start, end_date=end)
    mock_base.assert_called_with(cli.api_url_calendar, url_params={"start": "2020-06-13", "end": "2020-06-15"})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_command(mock_base, cli):
    res = cli.get_command()
    mock_base.assert_called_with(cli.api_url_command)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_command_with_id(mock_base, cli):
    res = cli.get_command("somecommand")
    mock_base.assert_called_with(cli.api_url_command + "/somecommand")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_post", return_value=TEST_JSON)
def test_syncrss(mock_base, cli):
    res = cli.sync_rss()
    mock_base.assert_called_with(cli.api_url_command, json_data={"name": "RssSync"})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_post", return_value=TEST_JSON)
def test_renamefiles(mock_base, cli):
    res = cli.rename_files([1, 2, 3])
    mock_base.assert_called_with(cli.api_url_command, json_data={"name": "RenameFiles", "files": [1, 2, 3]})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_diskspace(mock_base, cli):
    res = cli.get_disk_space()
    mock_base.assert_called_with(cli.api_url_diskspace)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=[TEST_JSON])
def test_rootfolder(mock_base, cli):
    res = cli.get_root_folder()
    mock_base.assert_called_with(cli.api_url_rootfolder)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_item(mock_base, cli):
    res = cli.get_item()
    mock_base.assert_called_with(cli.api_url_item)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_item_with_id(mock_base, cli):
    res = cli.get_item(item_id=1234)
    mock_base.assert_called_with(cli.api_url_item + "/1234")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=[TEST_JSON])
def test_lookup_item(mock_base, cli):
    res = cli.lookup_item("some keys")
    mock_base.assert_called_with(cli.api_url_itemlookup, url_params={"term": "some keys"})
    assert res == [TEST_JSON]


@patch("pycliarr.api.base_media.BaseCliApi.request_post", return_value=TEST_JSON)
def test_add_item(mock_base, cli):
    res = cli.add_item(TEST_JSON2)
    mock_base.assert_called_with(cli.api_url_item, json_data=TEST_JSON2)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_item(mock_base, cli):
    res = cli.delete_item(1234)
    mock_base.assert_called_with(cli.api_url_item + "/1234", {"deleteFiles": True})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_item_with_options(mock_base, cli):
    res = cli.delete_item(1234, delete_files=False, options={'a': 'b'})
    mock_base.assert_called_with(cli.api_url_item + "/1234", {"deleteFiles": False, 'a': 'b'})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_system_status(mock_base, cli):
    res = cli.get_system_status()
    mock_base.assert_called_with(cli.api_url_systemstatus)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_quality_profiles(mock_base, cli):
    res = cli.get_quality_profiles()
    mock_base.assert_called_with(cli.api_url_profile)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_queue(mock_base, cli):
    res = cli.get_queue()
    mock_base.assert_called_with(cli.api_url_queue)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_queue(mock_base, cli):
    res = cli.delete_queue(1234)
    mock_base.assert_called_with(cli.api_url_queue, {"id": 1234})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_queue_with_options(mock_base, cli):
    res = cli.delete_queue(1234, blacklist=True)
    mock_base.assert_called_with(cli.api_url_queue, {"id": 1234, "blacklist": True})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_history(mock_base, cli):
    res = cli.get_history()

    data = {"page": 1, "pageSize": 10, "sortKey": "date", "sortDir": "asc"}
    mock_base.assert_called_with(cli.api_url_history, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_history_with_options(mock_base, cli):
    res = cli.get_history(page=12, sort_key="abc", page_size=11, sort_dir="desc", options={'a': 'a'})

    data = {"page": 12, "pageSize": 11, "sortKey": "abc", "sortDir": "desc", 'a': 'a'}
    mock_base.assert_called_with(cli.api_url_history, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_logs(mock_base, cli):
    res = cli.get_logs()

    data = {"page": 1, "pageSize": 10, "sortKey": "time", "sortDir": "asc"}
    mock_base.assert_called_with(cli.api_url_log, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_logs_with_options(mock_base, cli):
    res = cli.get_logs(page=12, sort_key="abc", page_size=11, sort_dir="desc")

    data = {"page": 12, "pageSize": 11, "sortKey": "abc", "sortDir": "desc"}
    mock_base.assert_called_with(cli.api_url_log, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_backup(mock_base, cli):
    res = cli.get_backup()
    mock_base.assert_called_with(cli.api_url_systembackup)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_wanted(mock_base, cli):
    res = cli.get_wanted()

    data = {"page": 1, "pageSize": 10, "sortKey": "airDateUtc", "sortDir": "asc"}
    mock_base.assert_called_with(cli.api_url_wanted_missing, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_wanted_with_options(mock_base, cli):
    res = cli.get_wanted(page=12, sort_key="abc", page_size=11, sort_dir="desc")

    data = {"page": 12, "pageSize": 11, "sortKey": "abc", "sortDir": "desc"}
    mock_base.assert_called_with(cli.api_url_wanted_missing, url_params=data)
    assert res == TEST_JSON
