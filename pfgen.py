#!/usr/bin/env python

from __future__ import print_function

"""
Puppetfile generator
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

def importRepo(username, reponame, url, version, current_version):
    global debug, GH_TOKEN
    if debug:
        eprint("repo: "+username+"/"+reponame)
        eprint(str(locals()))


def importUser(username, repos, repo_pattern, skip_forked_repos, current_version):
    global debug, GH_TOKEN
    if debug:
        eprint("user: "+username)
        eprint(str(locals()))

    g = Github(GH_TOKEN)

    for repo in g.get_user(username).get_repos():
        if repo_pattern in repo.name:

            if debug:
                eprint("considering: "+repo.name+" - is fork? "+str(repo.fork))

            if skip_forked_repos and repo.fork:
                if debug:
                    eprint("skipping forked repo: {}".format(repo.name))
                continue


if __name__ == '__main__':
    try:
        basedir = sys.argv[1]
    except IndexError:
        basedir = '.'

    config = SafeConfigParser()
    config.read(basedir+'/pfgen.config')

    try:
        GH_TOKEN = config.get('github', 'token').strip('"').strip()
    except:
        sys.exit("ERROR: PAT is mandatory")

    try:
        debug = config.getboolean('github', 'debug')
    except:
        debug=False

    for section in config.sections():
        if section!="github":
            try:
                version=config.get(section, 'version').strip('"').strip()
            except:
                version=""
            try:
                current_version=config.getboolean(section, 'current-version')
            except:
                current_version=False
            if "/" in section:
                section_parts = section.split('/')
                username = section_parts[0]
                reponame = section_parts[1]
                try:
                    url=config.get(section, 'url').strip('"').strip()
                except:
                    url=""

                importRepo(username, reponame, url, version, current_version)
            else:
                username = section
                repos=[]
                try:
                    repo_pattern=config.get(section, 'repo-pattern').strip('"').strip()
                except:
                    repo_pattern=""
                try:
                    skip_forked_repos=config.getboolean(section, 'skip-forked-repos')
                except:
                    skip_forked_repos=False

                importUser(username, repos, repo_pattern, skip_forked_repos, current_version)
