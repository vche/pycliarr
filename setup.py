#!pyvenv/bin/python
from setuptools import find_packages, setup

import os
import distutils.cmd

class CleanCommand(distutils.cmd.Command):
    """
    Our custom command to clean out junk files.
    """
    description = "Cleans out junk files we don't want in the repo"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        cmd_list = dict(
            DS_Store="find . -name .DS_Store -print0 | xargs -0 rm -f;",
            pyc="find . -name '*.pyc' -exec rm -rf {} \;",
            egg="find . -name '*.egg-info' -exec rm -rf {} \;",
            cache="find ./src -name '__pycache__' -exec rm -rf {} \;",
            doc="rm -rf docs/doc/* docs/coverage/* \;",
        )
        for key, cmd in cmd_list.items():
            os.system(cmd)

# Most of the config is read from setup.cfg
setup(
    packages=find_packages(where="src", exclude=("test",)),
    package_dir={"": "src"},
    cmdclass={
        'clean': CleanCommand,
    },
)
