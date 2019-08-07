#!/usr/bin/env python

from __future__ import print_function

"""
Puppet Instance MANager
"""

import sh
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

    #
    # config comuna
    #

    try:
        base_dir = config.get('piman', 'base-dir').strip('"').strip("'").strip()
    except:
        sys.exit("ERROR: base-dir is mandatory")

    try:
        instance_template = config.get('piman', 'instance-template').strip('"').strip("'").strip()
    except:
        sys.exit("ERROR: instance-template is mandatory")

    try:
        puppet_fqdn = config.get('piman', 'puppet-fqdn').strip('"').strip("'").strip()
    except:
        sys.exit("ERROR: puppet-fqdn is mandatory")

    try:
        debug = config.getboolean('clickdownloader', 'debug')
    except:
        debug = False

    #
    # instances puppet
    #

    for instance in config.sections():
        if instance!="piman":

            if debug:
                print("= INSTANCE: "+instance)

            try:
                instance_config_remote = config.get(instance, 'config').strip('"').strip("'").strip()
            except:
                eprint("ERROR INSTANCE "+instance+": config is mandatory")

            try:
                instance_ssl_remote = config.get(instance, 'ssl').strip('"').strip("'").strip()
            except:
                eprint("ERROR INSTANCE "+instance+": ssl is mandatory")

            try:
                instance_instance_remote = config.get(instance, 'instance').strip('"').strip("'").strip()
            except:
                eprint("ERROR INSTANCE "+instance+": instance is mandatory")

            try:
                instance_files_remote = config.get(instance, 'files').strip('"').strip("'").strip()
            except:
                eprint("ERROR INSTANCE "+instance+": files is mandatory")

            instance_repo_path = base_dir+'/'+instance+'/instance'

            git = sh.git.bake(_cwd=instance_repo_path)

            if os.path.isdir(instance_repo_path+'/.git'):
                # repo ja colonat
            else:
                #clonar repo, importar desde template
                git.clone(instance_instance_remote)
                git.remote.add('origin', instance_template)
                git.pull('template', 'master')
