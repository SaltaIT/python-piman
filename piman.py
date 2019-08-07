#!/usr/bin/env python

from __future__ import print_function

"""
Puppet Instance MANager
"""

import os
import sys
import json
import argparse
from github import Github
from configparser import SafeConfigParser
from distutils.version import LooseVersion

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = './pfgen.config'

    config = SafeConfigParser()
    config.read(config_file)
