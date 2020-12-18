import pytest
from copy import deepcopy
from unittest.mock import patch
from pycliarr.api.sonarr import SonarrCli, SonarrSerieItem
from pycliarr.api.exceptions import SonarrCliError

TEST_JSON = {'somefield': "some value"}
TEST_SERIE = {'title': "some serie", "year": 2020}
TEST_HOST = "http://example.com"
TEST_APIKEY = "abcd1234"
TEST_SERIEINFO = {
    "title": "some serie",
    "alternateTitles": [],
    "sortTitle": "",
    "seasonCount": 0,
    "totalEpisodeCount": 0,
    "episodeCount": 0,
    "episodeFileCount": 0,
    "sizeOnDisk": 0,
    "status": "",
    "overview": "",
    "previousAiring": "",
    "network": "",
    "airTime": "",
    "images": [],
    "seasons": [],
    "year": 0,
    "path": "",
    "profileId": 0,
    "seasonFolder": True,
    "monitored": True,
    "useSceneNumbering": False,
    "runtime": 0,
    "tvdbId": 0,
    "tvRageId": 0,
    "tvMazeId": 0,
    "firstAired": "",
    "lastInfoSync": "",
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


@patch("pycliarr.api.sonarr.BaseCliMediaApi.get_root_folder", return_value={"path": "some/path/"})
@patch("pycliarr.api.sonarr.BaseCliMediaApi.request_get", return_value=TEST_SERIEINFO)
@patch("pycliarr.api.sonarr.BaseCliMediaApi.add_item", return_value=TEST_JSON)
def test_add_serie_withtvdb(mock_add, mock_root, mock_get, cli):
    exp = deepcopy(TEST_SERIEINFO)
    exp.update({
        "title": "some serie",
        "path": "some/path/some serie",
        "profileId": 1,
        "qualityProfileId": 1,
        "monitored": True,
        "addOptions": {
            "searchForMissingEpisodes": True,
            "ignoreEpisodesWithFiles": True,
            "ignoreEpisodesWithoutFiles": True,
        }
    })
    cli.add_serie(quality=1, tvdb_id=1234)
    mock_add.assert_called_with(json_data=exp)


@patch("pycliarr.api.sonarr.BaseCliMediaApi.get_root_folder", return_value={"path": "some/path/"})
@patch("pycliarr.api.sonarr.BaseCliMediaApi.add_item", return_value=TEST_JSON)
def test_add_serie_withinfo(mock_add, mock_root, cli):
    exp = deepcopy(TEST_SERIEINFO)
    exp.update({
        "title": "some serie",
        "path": "some/path/some serie",
        "profileId": 1,
        "qualityProfileId": 1,
        "monitored": False,
        "addOptions": {
            "searchForMissingEpisodes": False,
            "ignoreEpisodesWithFiles": True,
            "ignoreEpisodesWithoutFiles": True,
        }
    })
    info = SonarrSerieItem(title="some serie")
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
    mock_base.assert_called_with(1234, False, {"addExclusion": True})
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
