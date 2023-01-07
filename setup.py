#! /usr/bin/env python

import os
import glob
from setuptools import setup, find_packages

VERSION = "0.0.1"
try:
    import subprocess
    ver = VERSION + '-' + subprocess.check_output(['git', 'describe', '--abbrev=8', '--always', '--dirty', '--tags']).strip()
except:
    ver = VERSION
    print('Couldn\'t get version from git. Defaulting to %s' % ver)

# Generate a __version__.py file with this version in it
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'wr_cm', '__version__.py'), 'w') as fh:
    fh.write('__version__ = "%s"' % ver)

PACKAGES = find_packages()
print PACKAGES
REQUIRES = ["redis"]

setup_args = dict(name="wr_c_m",
                  maintainer="NRDZ Team",
                  description="Library for interfacing with the NRDZ White Rabbit nodes",
                  url="https://github.com/mruzinda/wr_c_m",
                  version=VERSION,
                  packages=PACKAGES,
                  package_data={'py7slib': [so.lstrip('py7slib') for so in glob.glob('py7slib/lib/*')]},
                  scripts=glob.glob('scripts/*'),
                  requires=REQUIRES)

if __name__ == '__main__':
    setup(**setup_args)
    if ver.endswith("dirty"):
        print "********************************************"
        print "* You are installing from a dirty git repo *"
        print "*      One day you will regret this.       *"
        print "*                                          *"
        print "*  Consider cleaning up and reinstalling.  *"
        print "********************************************"
