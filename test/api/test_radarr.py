import pytest
from copy import deepcopy
from unittest.mock import patch
from pycliarr.api.radarr import RadarrCli, RadarrMovieItem
from pycliarr.api.exceptions import RadarrCliError

TEST_JSON = {'somefield': "some value"}
TEST_MOVIE = {'title': "some movie", "year": 2020}
TEST_HOST = "http://example.com"
TEST_APIKEY = "abcd1234"
TEST_MOVIEINFO = {
    "title": "some movie",
    "sortTitle": "",
    "sizeOnDisk": 0,
    "status": "",
    "images": [],
    "downloaded": False,
    "year": 0,
    "hasFile": False,
    "path": "",
    "profileId": 0,
    "monitored": True,
    "minimumAvailability": "",
    "runtime": 0,
    "cleanTitle": "",
    "imdbId": "",
    "tmdbId": 0,
    "titleSlug": "",
    "genres": [],
    "tags": [],
    "added": "",
    "alternativeTitles": [],
    "qualityProfileId": 0,
    "id": 0,
    "overview": "",
    "inCinemas": "",
    "physicalRelease": "",
    "website": "",
    "youTubeTrailerId": "",
    "studio": "",
    "rootFolderPath": "",
    "isAvailable": "",
    "folderName": "",
    "certification": "",
    "ratings": {},
    "collection": {},
}

@pytest.fixture
def cli():
    return RadarrCli(TEST_HOST, TEST_APIKEY)


@patch("pycliarr.api.radarr.BaseCliMediaApi.get_item", return_value=TEST_MOVIE)
def test_get_movie(mock_base, cli):
    res = cli.get_movie()
    mock_base.assert_called_with(None)
    assert res.title == "some movie"
    assert res.year == 2020


@patch("pycliarr.api.radarr.BaseCliMediaApi.get_item", return_value=[TEST_MOVIE])
def test_get_movie_with_id(mock_base, cli):
    res = cli.get_movie(movie_id=1234)
    mock_base.assert_called_with(1234)
    assert res[0].title == "some movie"
    assert res[0].year == 2020


@patch("pycliarr.api.radarr.BaseCliMediaApi.lookup_item", return_value=[TEST_MOVIE, TEST_MOVIE])
def test_lookup_movie_with_term(mock_base, cli):
    res = cli.lookup_movie(term="some title")
    mock_base.assert_called_with("some title")
    assert res[0].title == "some movie"
    assert res[0].year == 2020


@patch("pycliarr.api.radarr.BaseCliMediaApi.lookup_item", return_value=[TEST_MOVIE])
def test_lookup_movie_with_term_single_res(mock_base, cli):
    res = cli.lookup_movie(term="some title")
    mock_base.assert_called_with("some title")
    assert res.title == "some movie"
    assert res.year == 2020


@patch("pycliarr.api.radarr.BaseCliMediaApi.request_get", return_value=TEST_MOVIE)
def test_lookup_movie_with_imdb(mock_base, cli):
    res = cli.lookup_movie(imdb_id="tt1234")
    mock_base.assert_called_with(f"{cli.api_url_itemlookup}/imdb", url_params={"imdbId": "tt1234"})
    assert res.title == "some movie"
    assert res.year == 2020


@patch("pycliarr.api.radarr.BaseCliMediaApi.request_get", return_value=TEST_MOVIE)
def test_lookup_movie_with_tmdb(mock_base, cli):
    res = cli.lookup_movie(tmdb_id=1234)
    mock_base.assert_called_with(f"{cli.api_url_itemlookup}/tmdb", url_params={"tmdbId": 1234})
    assert res.title == "some movie"
    assert res.year == 2020


@patch("pycliarr.api.radarr.BaseCliMediaApi.request_get", return_value=TEST_MOVIE)
def test_lookup_movie_with_all(mock_base, cli):
    res = cli.lookup_movie(term="some title", tmdb_id=1234, imdb_id="tt1234")
    mock_base.assert_called_with(f"{cli.api_url_itemlookup}/tmdb", url_params={"tmdbId": 1234})
    assert res.title == "some movie"
    assert res.year == 2020


def test_lookup_movie_with_noparam(cli):
    with pytest.raises(RadarrCliError):
        cli.lookup_movie()


@patch("pycliarr.api.radarr.BaseCliMediaApi.get_root_folder", return_value={"path": "some/path/"})
@patch("pycliarr.api.radarr.BaseCliMediaApi.request_get", return_value=TEST_MOVIEINFO)
@patch("pycliarr.api.radarr.BaseCliMediaApi.add_item", return_value=TEST_JSON)
def test_add_movie_withtmdb(mock_add, mock_root, mock_get, cli):
    exp = deepcopy(TEST_MOVIEINFO)
    exp.update({
        "title": "some movie",
        "path": "some/path/some movie",
        "profileId": 1,
        "qualityProfileId": 1,
        "monitored": True,
        "addOptions": {"searchForMovie": True}
    })
    cli.add_movie(quality=1, tmdb_id=1234)
    mock_add.assert_called_with(json_data=exp)


@patch("pycliarr.api.radarr.BaseCliMediaApi.get_root_folder", return_value={"path": "some/path/"})
@patch("pycliarr.api.radarr.BaseCliMediaApi.request_get", return_value=TEST_MOVIEINFO)
@patch("pycliarr.api.radarr.BaseCliMediaApi.add_item", return_value=TEST_JSON)
def test_add_movie_withimdb(mock_add, mock_root, mock_get, cli):
    exp = deepcopy(TEST_MOVIEINFO)
    exp.update({
        "title": "some movie",
        "path": "some/path/some movie",
        "profileId": 2,
        "qualityProfileId": 2,
        "monitored": True,
        "addOptions": {"searchForMovie": True}
    })
    cli.add_movie(quality=2, imdb_id="tt1234")
    mock_add.assert_called_with(json_data=exp)


@patch("pycliarr.api.radarr.BaseCliMediaApi.get_root_folder", return_value={"path": "some/path/"})
@patch("pycliarr.api.radarr.BaseCliMediaApi.add_item", return_value=TEST_JSON)
def test_add_movie_withinfo(mock_add, mock_root, cli):
    exp = deepcopy(TEST_MOVIEINFO)
    exp.update({
        "title": "some movie",
        "path": "some/path/some movie",
        "profileId": 1,
        "qualityProfileId": 1,
        "monitored": False,
        "addOptions": {"searchForMovie": False}
    })
    info = RadarrMovieItem(title="some movie")
    cli.add_movie(quality=1, movie_info=info, monitored=False, search=False)
    mock_add.assert_called_with(json_data=exp)


@patch("pycliarr.api.radarr.BaseCliMediaApi.request_get", return_value={})
def test_add_movie_noresults(mock_get, cli):
    with pytest.raises(RadarrCliError):
        cli.add_movie(quality=2, imdb_id="tt1234")


def test_add_movie_noparam(cli):
    with pytest.raises(RadarrCliError):
        cli.add_movie(quality=2)


@patch("pycliarr.api.radarr.BaseCliMediaApi.delete_item", return_value=TEST_JSON)
def test_delete_movie(mock_base, cli):
    res = cli.delete_movie(1234)
    mock_base.assert_called_with(1234, True, {})
    assert res == TEST_JSON


@patch("pycliarr.api.radarr.BaseCliMediaApi.delete_item", return_value=TEST_JSON)
def test_delete_movie_withoptions(mock_base, cli):
    res = cli.delete_movie(1234, delete_files=False, add_exclusion=True)
    mock_base.assert_called_with(1234, False, {"addExclusion": True})
    assert res == TEST_JSON


@patch("pycliarr.api.radarr.BaseCliMediaApi._sendCommand", return_value=TEST_JSON)
def test_refresh_movies(mock_base, cli):
    res = cli.refresh_movie()
    mock_base.assert_called_with({"name": "RefreshMovie"})
    assert res == TEST_JSON


@patch("pycliarr.api.radarr.BaseCliMediaApi._sendCommand", return_value=TEST_JSON)
def test_refresh_movie(mock_base, cli):
    res = cli.refresh_movie(1234)
    mock_base.assert_called_with({"name": "RefreshMovie", "movieId": 1234})
    assert res == TEST_JSON


@patch("pycliarr.api.radarr.BaseCliMediaApi._sendCommand", return_value=TEST_JSON)
def test_rescan_movies(mock_base, cli):
    res = cli.rescan_movie()
    mock_base.assert_called_with({"name": "RescanMovie"})
    assert res == TEST_JSON


@patch("pycliarr.api.radarr.BaseCliMediaApi._sendCommand", return_value=TEST_JSON)
def test_rescan_movie(mock_base, cli):
    res = cli.rescan_movie(1234)
    mock_base.assert_called_with({"name": "RescanMovie", "movieId": 1234})
    assert res == TEST_JSON
