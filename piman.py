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
import pfgen
import pickle
import string
import random
import getopt
import argparse
import datetime
import hieragen
import siteppgen
from io import StringIO
from pathlib import Path
from github import Github
from configparser import SafeConfigParser
from distutils.version import LooseVersion

def eprint(*args, **kwargs):
    ''' print to stderr'''
    print(*args, file=sys.stderr, **kwargs)

def save_puppet_details_to_file(fqdn, puppetmaster_port, puppetboard_port, projects_authstrings, filename):
    dict = {'fqdn': fqdn, 'puppetmaster_port': puppetmaster_port, 'puppetboard_port': puppetboard_port, 'projects_authstrings': projects_authstrings}
    file = open(filename, 'wb')
    pickle.dump(dict, file)
    file.close()

def load_puppet_details_to_file(filename):
    file = open(filename, 'rb')
    return pickle.load(file)

def load_proc_net_tcp():
    ''' Read the table of tcp connections & remove header  '''
    with open('/proc/net/tcp','r') as f:
        content = f.readlines()
        content.pop(0)
    return content

def _hex2dec(s):
    return str(int(s,16))

def _ip(s):
    ip = [(_hex2dec(s[6:8])),(_hex2dec(s[4:6])),(_hex2dec(s[2:4])),(_hex2dec(s[0:2]))]
    return '.'.join(ip)

def _convert_ip_port(array):
    host,port = array.split(':')
    return _ip(host),_hex2dec(port)

def _remove_empty(array):
    return [x for x in array if x !='']

def get_free_tcp_port(base_port):

    candidate_port = base_port

    proc_net_tcp = load_proc_net_tcp()
    tcp_listen_ports = []
    for line in proc_net_tcp:
        line_array = _remove_empty(line.split(' '))
        l_host,l_port = _convert_ip_port(line_array[1]) # Convert ipaddress and port from hex to decimal.

        # '0A':'LISTEN',
        if(line_array[3]=='0A'):
            tcp_listen_ports.append(l_port)

    # if debug:
    #     print(str(tcp_listen_ports))

    found_port=False
    while not found_port:
        for listen_port in tcp_listen_ports:
            # if debug:
            #     print(str(listen_port)+' vs '+candidate_port)
            if listen_port == candidate_port:
                candidate_port=candidate_port+1
                found_port=False
                break
        found_port=True

    return candidate_port

def randomStringDigits(size=10):
    lowercase_and_digits = string.ascii_lowercase + string.digits
    return ''.join(random.choice(lowercase_and_digits) for i in range(size))

def showJelp(msg):
    print("Usage:")
    print("   [-c|--config] <config file>")
    print("   [-h|--help]  -- show this message")
    print("");
    sys.exit(msg)

if __name__ == '__main__':

    config_file = './piman.config'
    auth_strings = []

    # parse opts
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'hlc:', [
                                                                    'help'
                                                                    'config=',
                                                                 ])
    except Exception as e:
        showJelp(str(e))


    for opt, arg in options:
        if opt in ('-h', '--help'):
            showJelp("unknow option")
        elif opt in ('-c', '--config'):
            config_file = arg
        #elif opt in ('-c', '--config'):
        else:
            showJelp("unknow option")

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

    try:
        pfgen_config = config.get('piman', 'pfgen-config')
    except:
        pfgen_config = './pfgen.config'

    try:
        hierayaml_config = config.get('piman', 'hierayaml-config')
    except:
        hierayaml_config = './hieragen.config'

    try:
        sitepp_config = config.get('piman', 'sitepp-config')
    except:
        sitepp_config = './siteppgen.config'

    try:
        enable_puppetboard = config.getboolean('piman', 'enable-puppetboard')
    except:
        enable_puppetboard = False

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

            try:
                projects = json.loads(config.get(instance,'projects'))
            except:
                projects = []

            try:
                append_random_string = config.getboolean(instance, 'projects-append-randomstring')
            except:
                append_random_string = True

            instance_repo_path = base_dir+'/'+instance+'/instance'
            os.makedirs(name=instance_repo_path, exist_ok=True)

            if debug:
                print("DEBUG: instance repo path: "+instance_repo_path)

            if os.path.isdir(instance_repo_path+'/.git'):
                # repo ja colonat
                if debug:
                    print(instance+': instance repo ja clonat: '+instance_repo_path)

                # update repo desde remote
                git_instance_repo = sh.git.bake(_cwd=instance_repo_path)
                git_instance_repo.pull('origin', 'master')

                saved_config = load_puppet_details_to_file(instance_repo_path+'/.piman.data')
                puppet_master_port = saved_config['puppetmaster_port']
                puppet_board_port = saved_config['puppetboard_port']
                projects_authstrings = saved_config['projects_authstrings']
            else:
                #clonar repo, importar desde template
                sh.git.clone(instance_instance_remote, instance_repo_path)

                # TODO: check si el repo remot ja conté dades

                git_instance_repo = sh.git.bake(_cwd=instance_repo_path)
                git_instance_repo.remote.add('template', instance_template)
                git_instance_repo.pull('template', 'master')

                sh.bash(instance_repo_path+'/update.utils.sh', _cwd=instance_repo_path)

                sh.cp(glob.glob(str(Path.home())+'/.ssh/id*a'), instance_repo_path+'/ssh')

                gitignore = open(instance_repo_path+"/.gitignore","w+")
                gitignore.write("*~\n")
                gitignore.write("*swp\n")
                gitignore.write("ssh/id_*\n")
                gitignore.write("utils/puppet-masterless\n")
                gitignore.write("utils/autocommit\n")
                gitignore.close()

                projects_authstrings=[]
                for project in projects:
                    projects_authstrings.append(project+'_'+randomStringDigits())

                puppet_master_port = get_free_tcp_port(base_port)
                puppet_board_port = get_free_tcp_port(int(puppet_master_port)+1)

                save_puppet_details_to_file(puppet_fqdn, puppet_master_port, puppet_board_port, projects_authstrings, instance_repo_path+'/.piman.data')

                if debug:
                    print(instance+': puppetmaster assigned port: '+puppet_master_port)
                    print(instance+': puppetboard assigned port: '+puppet_board_port)

                docker_compose_override = open(instance_repo_path+'/docker-compose.override.yml', "w+")
                docker_compose_override.write('version: "2.1"\n')
                docker_compose_override.write('services:\n')
                if enable_puppetboard:
                    docker_compose_override.write('  puppetboard:\n')
                    docker_compose_override.write('    ports:\n')
                    docker_compose_override.write('      - '+puppet_board_port+':80/tcp\n')
                docker_compose_override.write('  puppetdb:\n')
                docker_compose_override.write('    environment:')
                docker_compose_override.write("      EYP_PUPPETFQDN: '"+puppet_fqdn+"'\n")
                docker_compose_override.write("      EYP_PUPPETDB_EXTERNAL_PORT: '"+puppet_master_port+"'\n")
                docker_compose_override.write("  puppetmaster:\n")
                docker_compose_override.write("    ports:\n")
                docker_compose_override.write("      - "+puppet_master_port+":8140/tcp\n")
                docker_compose_override.write("    environment:")
                docker_compose_override.write("      EYP_PUPPETFQDN: '"+puppet_fqdn+"'\n")
                docker_compose_override.write("      EYP_PM_SSL_REPO: '"+instance_ssl_remote+"'\n")
                docker_compose_override.write("      EYP_PM_CUSTOMER_REPO: '"+instance_config_remote+"'\n")
                docker_compose_override.write("      EYP_PM_FILES_REPO: '"+instance_files_remote+"'\n")
                docker_compose_override.close()

                git_instance_repo.add('--all')
                git_instance_repo.commit('-vam', 'template')


                buf = StringIO()
                git_instance_repo('ls-remote', '--heads', 'origin', 'master',_out=buf)

                if debug:
                    print("ls-remote: >"+buf.getvalue()+"<")

                if buf.getvalue():
                    git_instance_repo.pull('origin', 'master', '--allow-unrelated-histories', '--no-edit')

                git_instance_repo.push('origin', 'master')


            # config repo
            config_repo_path = base_dir+'/'+instance+'/.tmp_config_repo'
            os.makedirs(name=config_repo_path, exist_ok=True)

            if debug:
                print("DEBUG: temporal config repo path: "+config_repo_path)

            git_config_repo = sh.git.bake(_cwd=config_repo_path)

            if os.path.isdir(config_repo_path+'/.git'):
                # repo ja colonat
                if debug:
                    print(instance+': config repo ja clonat: '+config_repo_path)
                git_config_repo.pull()

            else:
                if debug:
                    print(instance+': inicialitzant config repo: '+config_repo_path)
                sh.git.clone(instance_config_remote, config_repo_path)

            # Puppetfile
            if not os.path.isfile(config_repo_path+'/Puppetfile'):
                if debug:
                    print(instance+': generating Puppetfile')
                config_repo_puppetfile = open(config_repo_path+'/Puppetfile', "w+")
                pfgen.generatePuppetfile(config_file=pfgen_config, write_puppetfile_to=config_repo_puppetfile)
                config_repo_puppetfile.close()

            # site.pp
            if not os.path.isfile(config_repo_path+'/site.pp'):
                if debug:
                    print(instance+': generating site.pp')
                config_repo_sitepp = open(config_repo_path+'/site.pp', "w+")
                siteppgen.generatesitepp(config_file=sitepp_config, write_sitepp_to=config_repo_sitepp)
                config_repo_sitepp.close()

            # hiera.yaml
            if not os.path.isfile(config_repo_path+'/hiera.yaml'):
                if debug:
                    print(instance+': generating hiera.yaml')
                config_repo_hierayaml = open(config_repo_path+'/hiera.yaml', "w+")
                # TODO: afegir opció auth_strings - array per varis subprojectes
                hieragen.generatehierayaml(config_file=hierayaml_config, write_hierayaml_to=config_repo_hierayaml, hieradata_base_dir=config_repo_path+'/hieradata', puppet_fqdn=puppet_fqdn, puppet_port=puppet_master_port, create_skel_auth_strings=projects_authstrings)
                config_repo_hierayaml.close()

            git_config_repo.add('--all')
            try:
                git_config_repo.commit('-vam', 'piman '+datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))
            except:
                pass

            git_config_repo.push('origin', 'master')
