#!/usr/bin/env python
import re
import os
from setuptools import setup, find_packages

version_file = os.path.join(
    os.path.dirname(__file__),
    'mass_autoscaler',
    '__version__.py'
)

with open(version_file, 'r') as fp:
    m = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        fp.read(),
        re.MULTILINE
    )
    version = m.groups(1)[0]

setup(name='mass_autoscaler',
      version=version,
      license='MIT',
      url='https://github.com/mass-project/mass_autoscaler',
      install_requires=['docker', 'mass-api-client'],
      packages=find_packages(),
      )
