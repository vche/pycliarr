## pytemplate

Template for a pip python package with:
- tox pytest based unit tests
- pytest code coverage
- isort/black autoformat
- flake8 format checking
- mypy type checking
- sphinx doc generation

To use this template and create a new project:

```sh
git clone https://github.com/vche/pytemplate.git
./templatize.sh $NEW_PROJECT_NAME $NEW_PROJECT_PATH
```

The new project will be created in $NEW_PROJECT_PATH/$NEW_PROJECT_NAME
To run test and generate doc, see README


### Development

#### Installing sources projects

Get the project and create the virtual env:
```sh
git clone https://github.com/vche/pycliarr.git
virtualenv pyvenv
. pyvenv/bin/activate
pip install -e .
```

Note: Entry points will be installed in pyvenv/bin, libs with pyvenv libs

#### Run tests

```sh
pip install tox
tox
```

#### Generate documentation:

```sh
pip install sphinx sphinx_rtd_theme m2r
./setup.py doc
```

In case new classes/modules are added, update the autodoc list:
```sh
rm  docs/sphinx_conf/source/*
sphinx-apidoc -f -o docs/sphinx_conf/source/ src/pycliarr
```
