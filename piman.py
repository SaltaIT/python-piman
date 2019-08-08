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
    ''' print to stderr'''
    print(*args, file=sys.stderr, **kwargs)

TCP_ID_TO_STATE = {
        '01':'ESTABLISHED',
        '02':'SYN_SENT',
        '03':'SYN_RECV',
        '04':'FIN_WAIT1',
        '05':'FIN_WAIT2',
        '06':'TIME_WAIT',
        '07':'CLOSE',
        '08':'CLOSE_WAIT',
        '09':'LAST_ACK',
        '0A':'LISTEN',
        '0B':'CLOSING'
        }

def load_proc_net_tcp():
    ''' Read the table of tcp connections & remove header  '''
    with open(PROC_TCP,'r') as f:
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
    tcp_listen_ports = {}
    for line in content:
        line_array = _remove_empty(line.split(' '))
        l_host,l_port = _convert_ip_port(line_array[1]) # Convert ipaddress and port from hex to decimal.
        state = TCP_ID_TO_STATE[line_array[3]]
        pid = _get_pid_of_inode(inode)                  # Get pid prom inode.

        tcp_listen_ports['l_port'] = l_port
        tcp_listen_ports['state'] = state
        tcp_listen_ports['pid'] = pid

    found_port=False
    while not found_port:
        for listen_port in tcp_listen_ports:
            if listen_port['l_port'] == candidate_port:
                candidate_port=candidate_port+1
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
        debug = config.getboolean('clickdownloader', 'debug')
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
                print('repo ja clonat')
            else:
                #clonar repo, importar desde template
                sh.git.clone(instance_instance_remote, instance_repo_path)

                git_instance_repo = sh.git.bake(_cwd=instance_repo_path)
                git_instance_repo.remote.add('template', instance_template)
                git_instance_repo.pull('template', 'master')

                sh.bash(instance_repo_path+'/update.utils.sh')

                sh.cp('/root/.ssh/id*a', instance_repo_path+'/ssh')

                gitignore = open(instance_repo_path+"/.gitignore","w+")
                gitignore.write("*~")
                gitignore.write("*swp")
                gitignore.write("ssh/id_*")
                gitignore.write("utils/puppet-masterless")
                gitignore.write("utils/autocommit")
                gitignore.close()

                next_free_port = get_free_tcp_port(base_port)

                docker_compose_override = open(instance_repo_path+'/docker-compose.override.yml')
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
