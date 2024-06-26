import pytest
from copy import deepcopy
from unittest.mock import patch
from pycliarr.api.sonarr import SonarrCli, SonarrSerieItem
from pycliarr.api.exceptions import SonarrCliError

TEST_ROOT_PATH = [{"path": "some/path/", "id": 1}, {"path": "yet/otherpath/", "id": 3}]
TEST_JSON = {'somefield': "some value"}
TEST_SERIE = {'title': "some serie", "year": 2020}
TEST_HOST = "http://example.com"
TEST_APIKEY = "abcd1234"
TEST_SERIEINFO = {
    "title": "some serie",
    "alternateTitles": [],
    "sortTitle": "",
    "statistics": {},
    "status": "",
    "overview": "",
    "network": "",
    "airTime": "",
    "images": [],
    "seasons": [
        {"seasonNumber": 1, "monitored": True},
        {"seasonNumber": 2, "monitored": True},
        {"seasonNumber": 3, "monitored": True}
    ],
    "year": 0,
    "path": "",
    "seasonFolder": True,
    "monitored": True,
    "useSceneNumbering": False,
    "runtime": 0,
    "tvdbId": 0,
    "tvRageId": 0,
    "tvMazeId": 0,
    "firstAired": "",
    "seriesType": "",
    "cleanTitle": "",
    "imdbId": "",
    "titleSlug": "",
    "certification": "",
    "genres": [],
    "tags": [],
    "added": "",
    "ratings": {},
    "qualityProfileId": 0,
    "id": 0,
}


def new_serie_info():
    return deepcopy(TEST_SERIEINFO)


@pytest.fixture
def cli():
    return SonarrCli(TEST_HOST, TEST_APIKEY)


@patch("pycliarr.api.sonarr.BaseCliMediaApi.get_item", return_value=TEST_SERIE)
def test_get_serie(mock_base, cli):
    res = cli.get_serie()
    mock_base.assert_called_with(None)
    assert res.title == "some serie"
    assert res.year == 2020


@patch("pycliarr.api.sonarr.BaseCliMediaApi.get_item", return_value=[TEST_SERIE])
def test_get_serie_with_id(mock_base, cli):
    res = cli.get_serie(serie_id=1234)
    mock_base.assert_called_with(1234)
    assert res[0].title == "some serie"
    assert res[0].year == 2020


@patch("pycliarr.api.sonarr.BaseCliMediaApi.lookup_item", return_value=[TEST_SERIE, TEST_SERIE])
def test_lookup_serie_with_term(mock_base, cli):
    res = cli.lookup_serie(term="some title")
    mock_base.assert_called_with("some title")
    assert res[0].title == "some serie"
    assert res[0].year == 2020


@patch("pycliarr.api.sonarr.BaseCliMediaApi.lookup_item", return_value=[TEST_SERIE])
def test_lookup_serie_with_term_single_res(mock_base, cli):
    res = cli.lookup_serie(term="some title")
    mock_base.assert_called_with("some title")
    assert res.title == "some serie"
    assert res.year == 2020


@patch("pycliarr.api.sonarr.BaseCliMediaApi.lookup_item", return_value=TEST_SERIE)
def test_lookup_serie_with_tvdb(mock_base, cli):
    res = cli.lookup_serie(tvdb_id=1234)
    mock_base.assert_called_with("tvdb:1234")
    assert res.title == "some serie"
    assert res.year == 2020


@patch("pycliarr.api.sonarr.BaseCliMediaApi.lookup_item", return_value=TEST_SERIE)
def test_lookup_serie_with_all(mock_base, cli):
    res = cli.lookup_serie(term="some title", tvdb_id=1234)
    mock_base.assert_called_with("tvdb:1234")
    assert res.title == "some serie"
    assert res.year == 2020


def test_lookup_serie_with_noparam(cli):
    with pytest.raises(SonarrCliError):
        cli.lookup_serie()


@patch("pycliarr.api.sonarr.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=new_serie_info())
@patch("pycliarr.api.sonarr.BaseCliMediaApi.add_item", return_value=TEST_JSON)
def test_add_serie_withtvdb(mock_add, mock_root, mock_get, cli):
    exp = new_serie_info()
    exp.update({
        "title": "some serie",
        "path": "some/path/some serie",
        "qualityProfileId": 1,
        "monitored": True,
        "seasonFolder": False,
        "addOptions": {
            "searchForMissingEpisodes": True,
            "ignoreEpisodesWithFiles": True,
            "ignoreEpisodesWithoutFiles": True,
        }
    })
    cli.add_serie(quality=1, tvdb_id=1234, season_folder=False)
    mock_add.assert_called_with(json_data=exp)


@patch("pycliarr.api.sonarr.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=new_serie_info())
@patch("pycliarr.api.sonarr.BaseCliMediaApi.add_item", return_value=TEST_JSON)
def test_add_serie_withpath(mock_add, mock_root, mock_get, cli):
    exp = new_serie_info()
    exp.update({
        "title": "some serie",
        "path": "some/other_path/some_other_serie",
        "qualityProfileId": 1,
        "monitored": True,
        "seasonFolder": False,
        "addOptions": {
            "searchForMissingEpisodes": True,
            "ignoreEpisodesWithFiles": True,
            "ignoreEpisodesWithoutFiles": True,
        }
    })
    cli.add_serie(quality=1, tvdb_id=1234, season_folder=False, path="some/other_path/some_other_serie")
    mock_add.assert_called_with(json_data=exp)


@patch("pycliarr.api.sonarr.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=new_serie_info())
@patch("pycliarr.api.sonarr.BaseCliMediaApi.add_item", return_value=TEST_JSON)
def test_add_serie_withseasons(mock_add, mock_root, mock_get, cli):
    exp = new_serie_info()
    exp.update({
        "title": "some serie",
        "path": "some/path/some serie",
        "qualityProfileId": 1,
        "monitored": True,
        "seasons": [
            {"seasonNumber": 1, "monitored": True},
            {"seasonNumber": 2, "monitored": True},
            {"seasonNumber": 3, "monitored": False}
        ],
        "addOptions": {
            "searchForMissingEpisodes": True,
            "ignoreEpisodesWithFiles": True,
            "ignoreEpisodesWithoutFiles": False,
        }
    })
    cli.add_serie(quality=1, tvdb_id=1234, monitored_seasons=[1, 2])
    mock_add.assert_called_with(json_data=exp)


@patch("pycliarr.api.sonarr.BaseCliMediaApi.get_root_folder", return_value=TEST_ROOT_PATH)
@patch("pycliarr.api.sonarr.BaseCliMediaApi.add_item", return_value=TEST_JSON)
def test_add_serie_withinfo(mock_add, mock_root, cli):
    exp = new_serie_info()
    exp.update({
        "title": "some serie",
        "path": "some/path/some serie",
        "qualityProfileId": 1,
        "monitored": False,
        "addOptions": {
            "searchForMissingEpisodes": False,
            "ignoreEpisodesWithFiles": True,
            "ignoreEpisodesWithoutFiles": True,
        }
    })
    info = SonarrSerieItem(title="some serie")
    info.seasons = [
        {"seasonNumber": 1, "monitored": True},
        {"seasonNumber": 2, "monitored": True},
        {"seasonNumber": 3, "monitored": True}
    ]
    cli.add_serie(quality=1, serie_info=info, monitored=False, search=False)
    mock_add.assert_called_with(json_data=exp)


@patch("pycliarr.api.sonarr.BaseCliMediaApi.lookup_item", return_value={})
def test_add_serie_noresults(mock_get, cli):
    with pytest.raises(SonarrCliError):
        cli.add_serie(quality=2, tvdb_id=1234)


def test_add_serie_noparam(cli):
    with pytest.raises(SonarrCliError):
        cli.add_serie(quality=2)


@patch("pycliarr.api.sonarr.BaseCliMediaApi.delete_item", return_value=TEST_JSON)
def test_delete_serie(mock_base, cli):
    res = cli.delete_serie(1234)
    mock_base.assert_called_with(1234, True, {})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi.delete_item", return_value=TEST_JSON)
def test_delete_serie_withoptions(mock_base, cli):
    res = cli.delete_serie(1234, delete_files=False, add_exclusion=True)
    mock_base.assert_called_with(1234, False, {"addImportListExclusion": True})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi._sendCommand", return_value=TEST_JSON)
def test_refresh_series(mock_base, cli):
    res = cli.refresh_serie()
    mock_base.assert_called_with({"name": "RefreshSeries"})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi._sendCommand", return_value=TEST_JSON)
def test_refresh_serie(mock_base, cli):
    res = cli.refresh_serie(1234)
    mock_base.assert_called_with({"name": "RefreshSeries", "seriesId": 1234})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi._sendCommand", return_value=TEST_JSON)
def test_rescan_series(mock_base, cli):
    res = cli.rescan_serie()
    mock_base.assert_called_with({"name": "RescanSeries"})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi._sendCommand", return_value=TEST_JSON)
def test_rescan_serie(mock_base, cli):
    res = cli.rescan_serie(1234)
    mock_base.assert_called_with({"name": "RescanSeries", "seriesId": 1234})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=TEST_JSON)
def test_get_episode_with_serie(mock_base, cli):
    res = cli.get_episode(serie_id=1234)
    mock_base.assert_called_with(cli.api_url_episode, url_params={"seriesId": 1234})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=TEST_JSON)
def test_get_episode_with_episode(mock_base, cli):
    res = cli.get_episode(episode_id=1234)
    mock_base.assert_called_with(cli.api_url_episode + "/1234")
    assert res == TEST_JSON


def test_get_episode_noparam(cli):
    with pytest.raises(SonarrCliError):
        cli.get_episode()


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=TEST_JSON)
def test_get_episodefile_with_serie(mock_base, cli):
    res = cli.get_episode_file(serie_id=1234)
    mock_base.assert_called_with(cli.api_url_episodefile, url_params={"seriesId": 1234})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=TEST_JSON)
def test_get_episodefile_with_episode(mock_base, cli):
    res = cli.get_episode_file(episode_id=1234)
    mock_base.assert_called_with(cli.api_url_episodefile + "/1234")
    assert res == TEST_JSON


def test_get_episodefile_noparam(cli):
    with pytest.raises(SonarrCliError):
        cli.get_episode_file()


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_delete", return_value=TEST_JSON)
def test_delete_episode_file(mock_base, cli):
    res = cli.delete_episode_file(1234)
    mock_base.assert_called_with(cli.api_url_episodefile + "/1234")
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi.build_item_path")
def test_build_serie_path(mock_buildpath, cli):
    serie = SonarrSerieItem(title="some serie")
    cli.build_serie_path(serie)
    mock_buildpath.assert_called_with("some serie", 0)


@patch("pycliarr.api.sonarr.BaseCliMediaApi.build_item_path")
def test_build_serie_path_with_root(mock_buildpath, cli):
    serie = SonarrSerieItem(title="some serie")
    cli.build_serie_path(serie, 1)
    mock_buildpath.assert_called_with("some serie", 1)


@patch("pycliarr.api.sonarr.BaseCliMediaApi._sendCommand", return_value=TEST_JSON)
def test_search_missing(mock_base, cli):
    res = cli.missing_episodes_search()
    mock_base.assert_called_with({"name": "missingEpisodeSearch"})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_post", return_value={})
def test_create_exclusion(mock_post, cli):
    cli.create_exclusion("a title", 12345)
    mock_post.assert_called_with(
        cli.api_url_exclusions, json_data={"title": "a title", "tvdbId": 12345}
    )


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_put", return_value=TEST_JSON)
def test_edit_serie(mock_put, cli):
    serie = SonarrSerieItem(title="some serie")
    res = cli.edit_serie(serie)

    mock_put.assert_called_with(cli.api_url_item, json_data=serie.to_dict(), url_params=None)
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=TEST_JSON)
def test_get_queue(mock_get, cli):
    res = cli.get_queue()

    data = {
        "page": 1,
        "pageSize": 20,
        "sortKey": "progress",
        "sortDirection": "ascending",
        "includeUnknownSeriesItems": True,
    }
    mock_get.assert_called_with(cli.api_url_queue, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=TEST_JSON)
def test_get_queue_with_args(mock_get, cli):
    res = cli.get_queue(page = 2, sort_key = "sort", page_size = 3, sort_dir = "asc", include_unknown = False)

    data = {
        "page": 2,
        "pageSize": 3,
        "sortKey": "sort",
        "sortDirection": "asc",
        "includeUnknownSeriesItems": False,
    }
    mock_get.assert_called_with(cli.api_url_queue, url_params=data)
    assert res == TEST_JSON


@patch("pycliarr.api.base_media.BaseCliApi.request_post", return_value=TEST_JSON)
def test_renamefiles(mock_base, cli):
    res = cli.rename_files([1, 2, 3], 1)
    mock_base.assert_called_with(cli.api_url_command, json_data={"name": "RenameFiles", "files": [1, 2, 3], "seriesId": 1})
    assert res == TEST_JSON


@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get")
def test_get_rename_serie(mock_base, cli):
    res = cli.get_rename(1234)
    mock_base.assert_called_with(cli.api_url_rename, url_params={"seriesId": 1234})
