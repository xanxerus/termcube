#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

setup(
    name = "termcube",
    version = '0.1',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'termcube = termcube.termcube:main',
        ],
    },
)
