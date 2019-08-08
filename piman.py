#!/usr/bin/env python

from __future__ import print_function

"""
Puppet Instance MANager
"""

import sh
import os
import sys
import json
import glob
import argparse
from github import Github
from pathlib import Path
from configparser import SafeConfigParser
from distutils.version import LooseVersion

def eprint(*args, **kwargs):
    ''' print to stderr'''
    print(*args, file=sys.stderr, **kwargs)

def load_proc_net_tcp():
    ''' Read the table of tcp connections & remove header  '''
    with open('/proc/net/tcp','r') as f:
        content = f.readlines()
        content.pop(0)
    return content

def _get_pid_of_inode(inode):
    '''
    To retrieve the process pid, check every running process and look for one using
    the given inode.
    '''
    for item in glob.glob('/proc/[0-9]*/fd/[0-9]*'):
        try:
            if re.search(inode,os.readlink(item)):
                return item.split('/')[2]
        except:
            pass
    return None

def _hex2dec(s):
    return str(int(s,16))

def _ip(s):
    ip = [(_hex2dec(s[6:8])),(_hex2dec(s[4:6])),(_hex2dec(s[2:4])),(_hex2dec(s[0:2]))]
    return '.'.join(ip)

def _remove_empty(array):
    return [x for x in array if x !='']

def _convert_ip_port(array):
    host,port = array.split(':')
    return _ip(host),_hex2dec(port)

def get_free_tcp_port(base_port):

    candidate_port = base_port

    proc_net_tcp = load_proc_net_tcp()
    tcp_listen_ports = []
    for line in proc_net_tcp:
        line_array = _remove_empty(line.split(' '))
        l_host,l_port = _convert_ip_port(line_array[1]) # Convert ipaddress and port from hex to decimal.
        pid = _get_pid_of_inode(line_array[9])                  # Get pid prom inode.

        # '0A':'LISTEN',
        if(line_array[3]=='0A'):
            tcp_listen_ports.append(l_port)

    if debug:
        print(str(tcp_listen_ports))

    found_port=False
    while not found_port:
        for listen_port in tcp_listen_ports:
            if debug:
                print(str(listen_port)+' vs '+candidate_port)
            if listen_port == candidate_port:
                candidate_port=candidate_port+1
                found_port=False
                break
        found_port=True

    return candidate_port

if __name__ == '__main__':
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = './piman.config'

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
        debug = config.getboolean('piman', 'debug')
    except:
        debug = False

    try:
        base_port = config.get('piman', 'base-port')
    except:
        base_port = 8240

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

            os.makedirs(name=instance_repo_path, exist_ok=True)


            if debug:
                print("DEBUG: instance repo path: "+instance_repo_path)

            if os.path.isdir(instance_repo_path+'/.git'):
                # repo ja colonat
                if debug:
                    print(instance+': repo ja clonat')
            else:
                #clonar repo, importar desde template
                sh.git.clone(instance_instance_remote, instance_repo_path)

                git_instance_repo = sh.git.bake(_cwd=instance_repo_path)
                git_instance_repo.remote.add('template', instance_template)
                git_instance_repo.pull('template', 'master')

                sh.bash(instance_repo_path+'/update.utils.sh', _cwd=instance_repo_path)

                sh.cp(glob.glob(str(Path.home())+'/.ssh/id*a'), instance_repo_path+'/ssh')

                gitignore = open(instance_repo_path+"/.gitignore","w+")
                gitignore.write("*~")
                gitignore.write("*swp")
                gitignore.write("ssh/id_*")
                gitignore.write("utils/puppet-masterless")
                gitignore.write("utils/autocommit")
                gitignore.close()

                next_free_port = get_free_tcp_port(base_port)

                if debug:
                    print(instance+': assigned port: '+next_free_port)

                docker_compose_override = open(instance_repo_path+'/docker-compose.override.yml', "w+")
                gitignore.write('version: "2.1"')
                gitignore.write('services:')
                gitignore.write('  puppetdb:')
                gitignore.write('    environment:')
                gitignore.write("      EYP_PUPPETFQDN: '"+puppet_fqdn+"'")
                gitignore.write("      EYP_PUPPETDB_EXTERNAL_PORT: '"+next_free_port+"'")
                gitignore.write("  puppetmaster:")
                gitignore.write("    ports:")
                gitignore.write("      - "+next_free_port+":8140/tcp")
                gitignore.write("    environment:")
                gitignore.write("      EYP_PUPPETFQDN: '"+puppet_fqdn+"'")
                gitignore.write("      EYP_PM_SSL_REPO: '"+instance_ssl_remote+"'")
                gitignore.write("      EYP_PM_CUSTOMER_REPO: '"+instance_config_remote+"'")
                gitignore.write("      EYP_PM_FILES_REPO: '"+instance_files_remote+"'")
                docker_compose_override.close()

                git_instance_repo.add('--all')
                git_instance_repo.commit('-vam', 'template')
                git_instance_repo.pull('origin', 'master', '--allow-unrelated-histories', '--no-edit')
                git_instance_repo.push('origin', 'master')

                # config repo
                # Puppetfile
                # site.pp
                # hiera.yaml
