![GitHub](https://img.shields.io/github/license/vche/pycliarr) [![Codecov](https://img.shields.io/codecov/c/github/vche/pycliarr)](https://codecov.io/gh/vche/pycliarr) [![Read the Docs](https://img.shields.io/readthedocs/pycliarr)](https://pycliarr.readthedocs.io/en/latest/) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/vche/pycliarr)](https://github.com/vche/pycliarr/releases) [![PyPI](https://img.shields.io/pypi/v/pycliarr)](https://pypi.org/project/pycliarr/) [![Downloads](https://pepy.tech/badge/pycliarr)](https://pepy.tech/project/pycliarr)

## What's pycliarr

Python client for radarr and sonarr apis.
The package provides python client and CLI to use in command line.

[Documentation homepage](https://pycliarr.readthedocs.io/en/latest/)

## Usage

Sonarr CLI
```sh
pyvenv/bin/pycliarr -t "http://192.168.0.199:8989" -k "2ac2d8f667524da3bx1849e81dba5a84" -d sonarr get -i 65
pyvenv/bin/pycliarr -t "http://192.168.0.199:8989" -k "2ac2d8f667524da3bax849e81dba5a84" -d sonarr add -t "the walking dead"
```

Radarr CLI
```sh
pyvenv/bin/pycliarr -t "http://192.168.0.199:7878" -k "2ac2d8f667524da3bx1849e81dba5a84" -d radarr get -i 65
pyvenv/bin/pycliarr -t "http://192.168.0.199:7878" -k "2ac2d8f667524da3bax849e81dba5a84" -d radarr add -t "wonder woman"
```

Using radarr client
```python
from pycliarr.api.radarr import RadarrCli
radarr_cli = RadarrCli('192.168.0.199:7878', '5f5e32qf3ff8463e9f3d2388af0fd3e8')
radarr_cli.add_movie(imdb_id="tt1234", quality_profile=1)
movie = radarr_cli.get_movie(12)
print(movie.title)
```

Using sonarr client
```python
from pycliarr.api.sonarr import SonarrCli
sonarr_cli = SonarrCli('192.168.0.199:8989', '2ac2d8f667524da3bx1849e81dba5a84')
sonarr_cli.add_serie(imdb_id="tt1234", quality_profile=1)
serie = sonarr_cli.get_serie(12)
print(serie.title)
```

## CLI help

Clients:
```sh
pyvenv/bin/pycliarr --help
PyCliarr version 0.0.1
usage: pycliarr [-h] --host HOST --api-key API_KEY [--user USER] [--password PASSWORD] [--debug] {sonarr,radarr} ...

Radarr/Sonarr client

positional arguments:
  {sonarr,radarr}
    sonarr              use sonarr client
    radarr              use radarr client

optional arguments:
  -h, --help            show this help message and exit
  --host HOST, -t HOST  Host url, e.g 'http://192.168.0.1'
  --api-key API_KEY, -k API_KEY
                        API key, e.g '5f5e32xf3ff8463d9f1d2u88ef0fd3e8'
  --user USER, -u USER  Username if using basic authentication
  --password PASSWORD, -p PASSWORD
                        Password if using basic authentication
  --debug, -d           Enable debug logging
```

Radarr CLI:
```sh
pyvenv/bin/pycliarr radarr --help
PyCliarr version 0.0.1
usage: pycliarr radarr [-h] {get,delete,add,refresh,rescan,profiles,system-status,disk-space,queue,calendar,delqueue,wanted} ...

positional arguments:
  {get,delete,add,refresh,rescan,profiles,system-status,disk-space,queue,calendar,delqueue,wanted}
    get                 Get info on a of movie
    delete              Delete a movie
    add                 Add a movie from the imdb/tmdb id, or look for keywords
    refresh             Refresh movies
    rescan              Rescan movies
    profiles            Get list of quality profiles
    system-status       Get system status
    disk-space          Get disk space
    queue               Get current downloading queue
    calendar            Get events from calendar
    delqueue            Get list of quality profiles
    wanted              List wanted/missing

optional arguments:
  -h, --help            show this help message and exit
```

Sonarr CLI:
```sh
pyvenv/bin/pycliarr sonarr --help
PyCliarr version 0.0.1
usage: pycliarr sonarr [-h] {get,delete,add,refresh,rescan,get-episode,get-episode-file,delete-episode-file,profiles,system-status,disk-space,queue,calendar,delqueue,wanted} ...

positional arguments:
  {get,delete,add,refresh,rescan,get-episode,get-episode-file,delete-episode-file,profiles,system-status,disk-space,queue,calendar,delqueue,wanted}
    get                 Get info on a of serie
    delete              Delete a serie
    add                 Add a serie from the tvdb id, or look for keywords
    refresh             Refresh series
    rescan              Rescan series
    get-episode         Get info on an episode
    get-episode-file    Get info on an episode file
    delete-episode-file
                        Get info on a of serie
    profiles            Get list of quality profiles
    system-status       Get system status
    disk-space          Get disk space
    queue               Get current downloading queue
    calendar            Get events from calendar
    delqueue            Get list of quality profiles
    wanted              List wanted/missing

optional arguments:
  -h, --help            show this help message and exit
```
## Installation
From pip:
```sh
pip pycliarr
```

From git:
```sh
git clone https://github.com/vche/pycliarr.git
pip install -e .
```

## Development

### Installing sources projects

Get the project and create the virtual env:
```sh
git clone https://github.com/vche/pycliarr.git
virtualenv pyvenv
. pyvenv/bin/activate
pip install -e .
```

Note: Entry points will be installed in pyvenv/bin, libs with pyvenv libs

### Run tests

```sh
pip install tox
tox
```

### Generate documentation:

```sh
pip install sphinx sphinx_rtd_theme m2r
./setup.py doc
```

In case new classes/modules are added, update the autodoc list:
```sh
rm  docs/sphinx_conf/source/*
sphinx-apidoc -f -o docs/sphinx_conf/source/ src/pycliarr --separate
```
