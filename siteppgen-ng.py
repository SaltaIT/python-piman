#!/usr/bin/env python

from __future__ import print_function

"""
site.pp generator
"""

import os
import sys
import json
import argparse
from configparser import SafeConfigParser

debug = False
write_to = sys.stdout

def eprint(*args, **kwargs):
    global debug
    if debug:
        print(*args, file=sys.stderr, **kwargs)

def print_resource(resource_name, resource_alias):
    global debug, write_to

    # lookup( <NAME>, [<VALUE TYPE>], [<MERGE BEHAVIOR>], [<DEFAULT VALUE>] )
    # create_resources(postgresql::schema, $postgresschemas)
    print("create_resources("+resource_name+", $"+resource_alias+")", file=write_to)

def generatesitepp(config_file, write_sitepp_to=sys.stdout):
    global debug, write_to

    write_to=write_sitepp_to

    config = SafeConfigParser()
    config.read(config_file)

    try:
        debug = config.getboolean('sitegen', 'debug')
    except:
        debug = False

    try:
        resource_file = config.get('sitegen', 'resource-file').strip('"').strip("'").strip()
    except:
        resource_file = "./siteppgen/resource.list"

    try:
        resource_hash = json.loads(config.get('sitegen','resource-hash'))
    except:
        resource_hash = {}

    for resource_alias in resource_hash:
        # print resource hash
        print_resource(resource_hash[resource_alias], resource_alias)

    if not os.path.isfile(resource_file):
        eprint("WARNING: resource-file ("+resource_file+") not found, ignoring resources")

    with open(resource_file) as resource_file_handler:
       resource_name = resource_file_handler.readline().rstrip(os.linesep).strip('"').strip("'").strip()
       while resource_name:
           resource_alias = resource_name.strip(':').strip()+"s"
           print_resource(resource_name, resource_alias)
           resource_name = resource_file_handler.readline()

    try:
        deep_include_classes = json.loads(config.get('sitegen','deep-include-classes'))
    except:
        deep_include_classes = []

    # lookup('classes', Array[String], 'deep').include
    for deep_include_class in deep_include_classes:
        print("lookup('"+deep_include_class+"', Array[String], 'deep').include", file=write_to)


if __name__ == '__main__':
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = './siteppgen.config'
    generatesitepp(config_file=config_file)
