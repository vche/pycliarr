## What's pycliarr

Python client for radarr and sonarr apis.
The package provides python client and CLI to use in command line.

## Usage

Sonarr CLI
```sh
pyvenv/bin/pycliarr -t "http://192.168.0.199:8989" -k "2ac2d8f667524da3bx1849e81dba5a84" -d sonarr get -i 65
pyvenv/bin/pycliarr -t "http://192.168.0.199:8989" -k "2ac2d8f667524da3bax849e81dba5a84" -d sonarr add -t "the walking dead"
```

Radarr CLI
```sh
pyvenv/bin/pycliarr -t "http://192.168.0.199:8989" -k "2ac2d8f667524da3bx1849e81dba5a84" -d radarr get -i 65
pyvenv/bin/pycliarr -t "http://192.168.0.199:8989" -k "2ac2d8f667524da3bax849e81dba5a84" -d radarr add -t "wonder woman"
```

Using radarr client
```python
from pycliarr.api.radarr import RadarrCli
sonarr_cli = RadarrCli('192.168.0.199:7878', '5f5e32qf3ff8463e9f3d2388af0fd3e8')
sonarr_cli.add_movie(imdb_id="tt1234", quality_profile=1)
movie = sonarr_cli.get_movie(12)
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
sphinx-apidoc -f -o docs/sphinx_conf/source/ src/pycliarr
```
