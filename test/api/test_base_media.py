import pytest
from unittest.mock import patch
from pycliarr.api.base_media import BaseCliMediaApi
from pycliarr.api.exceptions import CliArrError
from datetime import datetime
from pathlib import Path

TEST_JSON = {'somefield': "some value"}
TEST_JSON2 = {'someotherfield': "some other value"}
TEST_HOST = "http://example.com"
TEST_APIKEY = "abcd1234"
TEST_ROOT_PATH = [{"path": "some/path/", "id": 1}, {"path": "yet/otherpath", "id": 3}]


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
    assert res == [TEST_JSON]


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
    data = {
        "page": 1,
        "pageSize": 20,
        "sortKey": "progress",
        "sortDirection": "ascending",
    }

    mock_base.assert_called_with(cli.api_url_queue, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_queue(mock_base, cli):
    res = cli.delete_queue(1234)
    mock_base.assert_called_with(f"{cli.api_url_queue}/1234", {})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_queue_with_options(mock_base, cli):
    res = cli.delete_queue(1234, blacklist=True)
    mock_base.assert_called_with(f"{cli.api_url_queue}/1234", {"blacklist": True})
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


@patch("pycliarr.api.base_media.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
def test_build_item_path_no_idx(mock_rootcli, cli):
    assert cli.build_item_path("some serie") == Path("some/path/some serie")


@patch("pycliarr.api.base_media.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
def test_build_item_path_idx(mock_rootcli, cli):
    assert cli.build_item_path("some serie", root_folder_id=3) == Path("yet/otherpath/some serie")


@patch("pycliarr.api.base_media.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
def test_build_item_path_bad_idx(mock_rootcli, cli):
    with pytest.raises(CliArrError):
        cli.build_item_path("some serie", root_folder_id=33)


@patch("pycliarr.api.base_media.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
def test_build_item_path_default_folder(mock_rootcli):
    cli = BaseCliMediaApi(TEST_HOST, TEST_APIKEY, default_root_folder_id=3)
    assert cli.build_item_path("some serie") == Path("yet/otherpath/some serie")


@patch("pycliarr.api.base_media.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
def test_build_item_path_default_folder_change(mock_rootcli):
    cli = BaseCliMediaApi(TEST_HOST, TEST_APIKEY, default_root_folder_id=1)
    cli.default_root_folder_id = 3
    assert cli.build_item_path("some serie") == Path("yet/otherpath/some serie")


@patch("pycliarr.api.base_media.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
def test_build_item_path_default_folder_with_folder(mock_rootcli):
    cli = BaseCliMediaApi(TEST_HOST, TEST_APIKEY, default_root_folder_id=1)
    assert cli.build_item_path("some serie", root_folder_id=3) == Path("yet/otherpath/some serie")


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_blocklist(mock_base, cli):
    res = cli.get_blocklist()
    data = {
                "page": 1,
                "pageSize": 20,
                "sortKey": "date",
                "sortDirection": "descending",
            }
    mock_base.assert_called_with(cli.api_url_blocklist, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_blocklist_paging(mock_base, cli):
    res = cli.get_blocklist(page=2, page_size=4, sort_key="title", sort_dir="ascending")
    data = {
                "page": 2,
                "pageSize": 4,
                "sortKey": "title",
                "sortDirection": "ascending",
            }
    mock_base.assert_called_with(cli.api_url_blocklist, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_blocklist(mock_base, cli):
    res = cli.delete_blocklist(3)
    mock_base.assert_called_with(cli.api_url_blocklist, url_params={"id": 3})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_blocklist_all(mock_base, cli):
    res = cli.delete_blocklist()
    mock_base.assert_called_with(f"{cli.api_url_blocklist}/bulk")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_notification_all(mock_base, cli):
    res = cli.get_notification()
    mock_base.assert_called_with(f"{cli.api_url_notification}/")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_notification(mock_base, cli):
    res = cli.get_notification(3)
    mock_base.assert_called_with(f"{cli.api_url_notification}/3")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_notification(mock_base, cli):
    res = cli.delete_notification(3)
    mock_base.assert_called_with(f"{cli.api_url_notification}/3")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_put", return_value=TEST_JSON)
def test_put_notification(mock_base, cli):
    res = cli.put_notification(3, {"test": "value"})
    mock_base.assert_called_with(f"{cli.api_url_notification}/3", json_data={"test": "value"})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_tag(mock_base, cli):
    res = cli.get_tag(3)
    mock_base.assert_called_with(f"{cli.api_url_tag}/3")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_tag_all(mock_base, cli):
    res = cli.get_tag()
    mock_base.assert_called_with(f"{cli.api_url_tag}/")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_delete", return_value=TEST_JSON)
def test_delete_tag(mock_base, cli):
    res = cli.delete_tag(3)
    mock_base.assert_called_with(f"{cli.api_url_tag}/3")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_put", return_value=TEST_JSON)
def test_edit_tag(mock_base, cli):
    res = cli.edit_tag(3, 'value')
    mock_base.assert_called_with(f"{cli.api_url_tag}/3", json_data={"id": 3, "label": "value"})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_post", return_value=TEST_JSON)
def test_create_tag(mock_base, cli):
    res = cli.create_tag('value')
    mock_base.assert_called_with(cli.api_url_tag, json_data={"id": 0, "label": "value"})
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_tag_detail(mock_base, cli):
    res = cli.get_tag_detail(3)
    mock_base.assert_called_with(f"{cli.api_url_tag}/detail/3")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_tag_detail_all(mock_base, cli):
    res = cli.get_tag_detail()
    mock_base.assert_called_with(f"{cli.api_url_tag}/detail/")
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_get", return_value=TEST_JSON)
def test_get_language_profiles(mock_base, cli):
    res = cli.get_language_profiles()
    mock_base.assert_called_with(cli.api_url_language_profile)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliMediaApi.request_get", return_value={})
def test_get_exclusion(mock_post, cli):
    cli.get_exclusion(12345)
    mock_post.assert_called_with(f"{cli.api_url_exclusions}/12345")


@patch("pycliarr.api.base_media.BaseCliMediaApi.request_get", return_value={})
def test_get_exclusion_all(mock_post, cli):
    cli.get_exclusion()
    mock_post.assert_called_with(f"{cli.api_url_exclusions}/")


@patch("pycliarr.api.base_media.BaseCliMediaApi.request_delete", return_value={})
def test_delete_exclusion(mock_post, cli):
    cli.delete_exclusion(12345)
    mock_post.assert_called_with(f"{cli.api_url_exclusions}/12345")
