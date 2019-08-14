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

def generatesitepp(config_file, write_sitepp_to=sys.stdout):
    global debug, write_to

    write_to=write_sitepp_to

    config = SafeConfigParser()
    config.read(config_file)

    try:
        debug = config.getboolean('sitegen', 'debug')
    except:
        debug = False

    print('''
#
# file
#

$files = hiera_hash('files', {})
create_resources(file, $files)

#
# cron
#

create_resources(cron, hiera_hash('cronjobs', {}))
create_resources(cron, hiera_hash('crontabs', {}))


#
# package
#

$common_packages = hiera('paquets_general', [])
package { $common_packages:
	ensure => 'installed',
}

$paquets = hiera('paquets', [])
package { $paquets:
        ensure => 'installed',
}

#base_packages
$base_packages = hiera_hash('base_packages', {})
create_resources(package, $base_packages)

#
# yumrepo
#

$yumrepos = hiera_hash('yumrepo', {})
create_resources(yumrepo, $yumrepos)

create_resources(yumrepo, hiera_hash('yumrepos', {}))

#
# service
#

create_resources(service, hiera_hash('services', {}))

#
# /etc/hosts
#

$etchosts= hiera_hash('etchosts', {})
create_resources(host, $etchosts)


#
# ssh_authorized_key
#

$sshkeys = hiera_hash('sshkeys', {})
create_resources(ssh_authorized_key, $sshkeys)

#
# sshkey
#

$knownhosts= hiera_hash('knownhosts', {})
create_resources(sshkey, $knownhosts)

#
# eyp-audit
#

$fsrules= hiera_hash('fsrules', {})
create_resources(audit::fsrule, $fsrules)

$syscallrules= hiera_hash('syscallrules', {})
create_resources(audit::syscallrule, $syscallrules)

create_resources(audit::fsrule, hiera_hash('auditfsrules', {}))
create_resources(audit::syscallrule, hiera_hash('auditsyscallrules', {}))


#
# eyp-openssh
#

$sshprivkeys = hiera_hash('sshprivkeys', {})
create_resources(openssh::privkey, $sshprivkeys)

$sshmatch = hiera_hash('sshmatch', {})
create_resources(openssh::match, $sshmatch)



#
# user
#

$users = hiera_hash('users', {})
create_resources(user, $users)

#
# group
#

$groups = hiera_hash('groups', {})
create_resources(group, $groups)


#
# mount
#

$plain_mounts = hiera_hash('plain_mounts', {})
create_resources(mount, $plain_mounts)

$mounts = hiera_hash('mounts', {})
create_resources(mount, $mounts)


#
# exec
#

$plain_execs = hiera_hash('plain_execs', {})
create_resources(exec, $plain_execs)


#
# eyp-proftpd
#


$ftpusers = hiera('ftpusers', {})
create_resources(proftpd::user, $ftpusers)

#
# eyp-sudoers
#


$sudos = hiera_hash('sudos', {})
create_resources(sudoers::sudo, $sudos)

#
# eyp-named
#

$zones = hiera_hash('zones', {})
create_resources(named::zone, $zones)

#
# puppetlabs-apt
#

$ppas = hiera('ppas', {})
create_resources(apt::ppa, $ppas)

#
# eyp-nodejs
#

$npmpackages = hiera('npmpackages', {})
create_resources(npmpackage, $npmpackages)

#
# eyp-prurgefiles
#

$purgefiles= hiera_hash('purgefiles', {})
create_resources(purgefiles::cronjob, $purgefiles)

#
# eyp-logrotate
#

$logrotates_common = hiera_hash('logrotates_common', {})
create_resources(logrotate::logs, $logrotates_common)

$logrotates = hiera_hash('logrotates', {})
create_resources(logrotate::logs, $logrotates)

#
# eyp-mysql
#

$mysqldump= hiera('mysqldump', {})
create_resources(mysql::backupmysqldump, $mysqldump)

$mysqldbs = hiera('mysqldbs', {})
create_resources(mysql_database, $mysqldbs)

$xtrabackup= hiera_hash('xtrabackup', {})
create_resources(mysql::backup::xtrabackup, $xtrabackup)

$mysqlcommunityinstances = hiera_hash('mysqlcommunityinstances', {})
create_resources(mysql::community::instance, $mysqlcommunityinstances)

$mysqlxtradbclusterinstances = hiera_hash('mysqlxtradbclusterinstances', {})
create_resources(mysql::xtradbcluster::instance, $mysqlxtradbclusterinstances)

create_resources(mysql::mycnf, hiera_hash('mysqlmycnfs', {}))
create_resources(mysql::mycnf::mysqld, hiera_hash('mysqlmycnfmysqlds', {}))
create_resources(mysql::mycnf::client, hiera_hash('mysqlmycnfclients', {}))


#
# eyp-couchbase
#

$cbbackup = hiera_hash('cbbackup', {})
create_resources(couchbase::backupscript, $cbbackup)

#
# eyp-monit
#

$monitchecks= hiera_hash('monitchecks', {})
create_resources(monit::checkscript, $monitchecks)

#
# eyp-udev
#

$udevrules = hiera_hash('udevrules', {})
create_resources(udev::interface, $udevrules)

#
# eyp-wordpress
#

$wpsites= hiera_hash('wpsites', {})
create_resources(wordpress::site, $wpsites)

#
# eyp-apache
#

$apachevhosts= hiera('apachevhosts', {})
create_resources(apache::vhost, $apachevhosts)

$apachecerts= hiera('apachecerts', {})
create_resources(apache::cert, $apachecerts)

$apachecustomconfs= hiera('apachecustomconfs', {})
create_resources(apache::custom_conf, $apachecustomconfs)

$apacheserverstatus = hiera('apacheserverstatus', {})
create_resources(apache::serverstatus, $apacheserverstatus)

$apacheredirects= hiera('apacheredirects', {})
create_resources(apache::redirect, $apacheredirects)

$apachedirectories= hiera('apachedirectories', {})
create_resources(apache::directory, $apachedirectories)

$apachelocations= hiera('apachelocations', {})
create_resources(apache::location, $apachelocations)

$apachebalancers= hiera_hash('apachebalancers', {})
create_resources(apache::mod::proxy::balancer, $apachebalancers)

$apacheproxypasses= hiera_hash('apacheproxypasses', {})
create_resources(apache::mod::proxy::proxypass, $apacheproxypasses)

$apachedavsvnrepos= hiera_hash('apachedavsvnrepos', {})
create_resources(apache::davsvnrepo, $apachedavsvnrepos)

$apachemodules= hiera_hash('apachemodules', {})
create_resources(apache::module, $apachemodules)

$apacheheaders= hiera_hash('apacheheaders', {})
create_resources(apache::header, $apacheheaders)

$apacheincludesconf= hiera_hash('apacheincludesconf', {})
create_resources(apache::include_conf, $apacheincludesconf)

$apacheaddtypes= hiera_hash('apacheaddtypes', {})
create_resources(apache::addtype, $apacheaddtypes)

$apachesslproxies= hiera_hash('apachesslproxies', {})
create_resources(apache::sslproxy, $apachesslproxies)

$apacherequestheaders= hiera_hash('apacherequestheaders', {})
create_resources(apache::requestheader, $apacherequestheaders)

$apachefilesmatches= hiera_hash('apachefilesmatches', {})
create_resources(apache::filesmatch, $apachefilesmatches)

$apachelogformats= hiera_hash('apachelogformats', {})
create_resources(apache::logformat, $apachelogformats)

$apachevhostadauths= hiera_hash('apachevhostadauths', {})
create_resources(apache::vhost::adauth, $apachevhostadauths)


#
# eyp-nginx
#

$nginxvhosts= hiera_hash('nginxvhosts', {})
create_resources(nginx::vhost, $nginxvhosts)

$nginxproxypass= hiera_hash('nginxproxypass', {})
create_resources(nginx::proxypass, $nginxproxypass)

$nginxstubstatus= hiera_hash('nginxstubstatus', {})
create_resources(nginx::stubstatus, $nginxstubstatus)

create_resources(nginx::custom_conf, hiera_hash('nginxcustomconfs', {}))

create_resources(nginx::cert, hiera_hash('nginxcerts', {}))

create_resources(nginx::proxyredirect, hiera_hash('nginxproxyredirects', {}))

create_resources(nginx::redirect, hiera_hash('nginxredirects', {}))

create_resources(nginx::htuser, hiera_hash('nginxhtusers', {}))

create_resources(nginx::location, hiera_hash('nginxlocations', {}))

#
# eyp-logstash
#

$logstashtcpinputs= hiera('logstashtcpinputs', {})
create_resources(logstash::tcpinput, $logstashtcpinputs)

$logstashinputs = hiera('logstashinputs', {})
create_resources(logstash::input, $logstashinputs)

$logstashoutputs = hiera('logstashoutputs', {})
create_resources(logstash::output, $logstashoutputs)

$logstashjsonfilters = hiera('logstashjsonfilters', {})
create_resources(logstash::jsonfilter, $logstashjsonfilters)

$logstashaddconf= hiera('logstashaddconf', {})
create_resources(logstash::addconf, $logstashaddconf)

$logstashplugins= hiera('logstashplugins', {})
create_resources(logstash_plugin, $logstashplugins)

create_resources(logstash::output::elasticsearch, hiera_hash('logstashoutputselasticsearch', {}))

create_resources(logstash::input::file, hiera_hash('logstashinputfiles', {}))

#
# eyp-rsyslog
#

$rsyslogfacilities = hiera('rsyslogfacilities', {})
create_resources(rsyslog::facility, $rsyslogfacilities)

$rsyslogimfiles= hiera('rsyslogimfiles', {})
create_resources(rsyslog::imfile, $rsyslogimfiles)

$rsyslogimtcp= hiera('rsyslogimtcp', {})
create_resources(rsyslog::imtcp, $rsyslogimtcp)

$rsyslogimudp= hiera('rsyslogimudp', {})
create_resources(rsyslog::imudp, $rsyslogimudp)


#
# eyp-pam
#

$security_limits = hiera_hash('security_limits', {})
create_resources(pam::limit, $security_limits)

$securettys= hiera_hash('securettys', {})
create_resources(pam::securetty, $securettys)


#
# eyp-tomcat
#

$tomcatinstances = hiera_hash('tomcatinstances', {})
create_resources(tomcat::instance, $tomcatinstances)

$tomcatusers= hiera_hash('tomcatusers', {})
create_resources(tomcat::tomcatuser, $tomcatusers)

$jndiproperties= hiera('jndiproperties', {})
create_resources(tomcat::jndi, $jndiproperties)

$jaasproperties= hiera('jaasproperties', {})
create_resources(tomcat::jaas, $jaasproperties)

$tomcatlibs= hiera('tomcatlibs', {})
create_resources(tomcat::lib, $tomcatlibs)

$tomcatlibstarballs= hiera('tomcatlibstarballs', {})
create_resources(tomcat::libstarball, $tomcatlibstarballs)

$tomcatauthenticators= hiera('tomcatauthenticators', {})
create_resources(tomcat::authenticators, $tomcatauthenticators)

$tomcatproperties = hiera('tomcatproperties', {})
create_resources(tomcat::properties, $tomcatproperties)

$tomcatwebxml = hiera('tomcatwebxml', {})
create_resources(tomcat::webxml, $tomcatwebxml)

$tomcatcontext= hiera('tomcatcontext', {})
create_resources(tomcat::context, $tomcatcontext)

$tomcatcontextxml= hiera_hash('tomcatcontextxml', {})
create_resources(tomcat::contextxml, $tomcatcontextxml)

$tomcatcontextxmlenvs= hiera_hash('tomcatcontextxmlenvs', {})
create_resources(tomcat::contextxml::environment, $tomcatcontextxmlenvs)

$tomcatcontextxmlreslinks= hiera_hash('tomcatcontextxmlreslinks', {})
create_resources(tomcat::contextxml::resourcelink, $tomcatcontextxmlreslinks)

$tomcatresources= hiera_hash('tomcatresources', {})
create_resources(tomcat::resource, $tomcatresources)

$tomcatdriverpostgres=hiera_hash('tomcatdriverpostgres', {})
create_resources(tomcat::driver::postgres, $tomcatdriverpostgres)

$tomcatrealmjndi=hiera_hash('tomcatrealmjndi', {})
create_resources(tomcat::realm::jndi, $tomcatrealmjndi)

$tomcatcatalinapolicies=hiera_hash('tomcatcatalinapolicies', {})
create_resources(tomcat::catalinapolicy, $tomcatcatalinapolicies)

$tomcatkerberos=hiera_hash('tomcatkerberos', {})
create_resources(tomcat::krb5, $tomcatkerberos)

$tomcatlogin=hiera_hash('tomcatlogin', {})
create_resources(tomcat::login, $tomcatlogin)

$tomcatdepolywars=hiera_hash('tomcatdepolywars', {})
create_resources(tomcat::deploywar, $tomcatdepolywars)

$tomcatagents=hiera_hash('tomcatagents', {})
create_resources(tomcat::agent, $tomcatagents)

$tomcatvalves=hiera_hash('tomcatvalves', {})
create_resources(tomcat::valve, $tomcatvalves)

$tomcatjvmproperties=hiera_hash('tomcatjvmproperties', {})
create_resources(tomcat::jvmproperty, $tomcatjvmproperties)

$tomcatjavaproperties=hiera_hash('tomcatjavaproperties', {})
create_resources(tomcat::java_property, $tomcatjavaproperties)

create_resources(tomcat::cert, hiera_hash('tomcatcerts', {}))

create_resources(tomcat::cacert, hiera_hash('tomcatcacerts', {}))

#
# eyp-php
#

$phpmodules = hiera('phpmodules', {})
create_resources(php::module, $phpmodules)

$peclmodules = hiera('peclmodules', {})
create_resources(php::pecl, $peclmodules)

$twig = hiera('twig', {})
create_resources(php::twig, $twig)

$maxmind = hiera('maxmind', {})
create_resources(php::maxmind, $maxmind)

$phpcouchbase = hiera('phpcouchbase', {})
create_resources(php::peclcouchbase, $phpcouchbase)

$enablemodule = hiera('enablemodule', {})
create_resources(php::enablemodule, $enablemodule)

$phpenablemodules = hiera_hash('phpenablemodules', {})
create_resources(php::enablemodule, $phpenablemodules)

$fpm = hiera('fpm', {})
create_resources(php::fpm, $fpm)

$fpmpool = hiera('fpmpool', {})
create_resources(php::fpmpool, $fpmpool)

$phpmysqlndmsdatasources = hiera_hash('phpmysqlndmsdatasources', {})
create_resources(php::mysqlnd_ms::datasource, $phpmysqlndmsdatasources)

$phpmysqlndmsmasters = hiera_hash('phpmysqlndmsmasters', {})
create_resources(php::mysqlnd_ms::master, $phpmysqlndmsmasters)

$phpmysqlndmsslaves = hiera_hash('phpmysqlndmsslaves', {})
create_resources(php::mysqlnd_ms::slave, $phpmysqlndmsslaves)


#
# eyp-network
#

$routes = hiera('routes', {})
create_resources(network::route, $routes)

$eths	= hiera('eths', {})
create_resources(network::interface, $eths)


#
# eyp-openldap
#

$ldapbackups= hiera('ldapbackups', {})
create_resources(openldap::backupscript, $ldapbackups)

#
# eyp-postgresql
#

$hbarules= hiera_hash('hbarules', {})
create_resources(postgresql::hba_rule, $hbarules)

$postgresroles= hiera_hash('postgresroles', {})
create_resources(postgresql::role, $postgresroles)

$postgresschemas= hiera_hash('postgresschemas', {})
create_resources(postgresql::schema, $postgresschemas)

create_resources(postgresql::db, hiera_hash('postgresdbs', {}))

create_resources(postgresql::pgdumpbackup, hiera_hash('pgdumpbackups', {}))


#
# eyp-barman
#

$barmanbackups= hiera_hash('barmanbackups', {})
create_resources(barman::backup, $barmanbackups)


#
# eyp-sysctl
#

$sysctlset = hiera_hash('sysctlset', {})
create_resources(sysctl::set, $sysctlset)

#
# eyp-iscsi
#

$interfaceiscsi= hiera_hash('interfaceiscsi', {})
create_resources(iscsi::interface, $interfaceiscsi)

$sessions_iscsi= hiera_hash('sessions_iscsi', {})
create_resources(iscsi::session, $sessions_iscsi)

$iscsidiscovery=hiera_hash('iscsidiscovery', {})
create_resources(iscsi::discovery, $iscsidiscovery)

$iscsiinterfaces=hiera_hash('iscsiinterfaces', {})
create_resources(iscsi::interface, $iscsiinterfaces)


#
# eyp-multipathd
#

$lun_alias= hiera_hash('lun_alias', {})
create_resources(multipathd::alias, $lun_alias)

#
# eyp-nfs
#

$nfsmounts=hiera_hash('nfsmounts', {})
create_resources(nfs::nfsmount, $nfsmounts)

$nfsexports=hiera_hash('nfsexports', {})
create_resources(nfs::export, $nfsexports)


#
# eyp-oracle
#

$oraclecompatpackages=hiera_hash('oraclecompatpackages', {})
create_resources(oracle::compat::package, $oraclecompatpackages)

$oracleconstrings=hiera_hash('oracleconstrings', {})
create_resources(oracleclient::connectstring, $oracleconstrings)

#
# eyp-bash
#

$bashenvs=hiera_hash('bashenvs', {})
create_resources(bash::environment, $bashenvs)

$bashumasks=hiera_hash('bashumasks', {})
create_resources(bash::umask, $bashumasks)

$bashprompts=hiera_hash('bashprompts', {})
create_resources(bash::prompt, $bashprompts)

$bashaliases=hiera_hash('bashaliases', {})
create_resources(bash::alias, $bashaliases)


#
# eyp-modprobe
#

$modprobeinstall=hiera_hash('modprobeinstall', {})
create_resources(modprobe::install, $modprobeinstall)

create_resources(modprobe::option, hiera_hash('modprobeoptions', {}))

#
# eyp-postfix
#

$postfixtransports=hiera_hash('postfixtransports', {})
create_resources(postfix::transport, $postfixtransports)

$postfixvmailaccounts=hiera_hash('postfixvmailaccounts', {})
create_resources(postfix::vmail::account, $postfixvmailaccounts)

$postfixvmailalias=hiera_hash('postfixvmailalias', {})
create_resources(postfix::vmail::alias, $postfixvmailalias)

$postfixsendercanonicalmaps=hiera_hash('postfixsendercanonicalmaps', {})
create_resources(postfix::sendercanonicalmap, $postfixsendercanonicalmaps)

$postfixgenericmaps=hiera_hash('postfixgenericmaps', {})
create_resources(postfix::genericmap, $postfixgenericmaps)

$postfixinstances=hiera_hash('postfixinstances', {})
create_resources(postfix::instance, $postfixinstances)


#
# eyp-rsync
#

$scheduledrsyncs=hiera_hash('scheduledrsyncs', {})
create_resources(rsync::scheduledrsync, $scheduledrsyncs)

#
# eyp-crond
#

$grantusercron=hiera_hash('grantusercron', {})
create_resources(crond::grantuser, $grantusercron)

#
# eyp-squid
#

$squiddomain=hiera_hash('squiddomain', {})
create_resources(squid::domain, $squiddomain)

$squidlogformats=hiera_hash('squidlogformats', {})
create_resources(squid::logformat, $squidlogformats)

$squidaccesslogs=hiera_hash('squidaccesslogs', {})
create_resources(squid::accesslog, $squidaccesslogs)

$squidacls=hiera_hash('squidacls', {})
create_resources(squid::acl, $squidacls)

$squidhttpaccess=hiera_hash('squidhttpaccess', {})
create_resources(squid::httpaccess, $squidhttpaccess)

create_resources(squid::followxff, hiera_hash('squidfollowxffs', {}))

#
# eyp-cups //*//
#

$cupsdummyqueue=hiera_hash('cupsdummyqueue', {})
create_resources(cups::dummyqueue, $cupsdummyqueue)

#
# eyp-xvfb
#

$xvfbinstances=hiera_hash('xvfbinstances', {})
create_resources(xvfb::instance, $xvfbinstances)

#
# eyp-tarbackup
#

$tarbackupinstances=hiera_hash('tarbackupinstances', {})
create_resources(tarbackup::instance, $tarbackupinstances)

#
# eyp-bacula
#

$baculasddevices=hiera_hash('baculasddevices', {})
create_resources(bacula::sd::device, $baculasddevices)

$baculasdautochangers=hiera_hash('baculasdautochangers', {})
create_resources(bacula::sd::autochanger, $baculasdautochangers)

$baculadircatalogs=hiera_hash('baculadircatalogs', {})
create_resources(bacula::dir::catalog, $baculadircatalogs)

$baculadirfilesets=hiera_hash('baculadirfilesets', {})
create_resources(bacula::dir::fileset, $baculadirfilesets)

$baculadirschedules=hiera_hash('baculadirschedules', {})
create_resources(bacula::dir::schedule, $baculadirschedules)

$baculadirclients=hiera_hash('baculadirclients', {})
create_resources(bacula::dir::client, $baculadirclients)

$baculadirstorages=hiera_hash('baculadirstorages', {})
create_resources(bacula::dir::storage, $baculadirstorages)

$baculadirpools=hiera_hash('baculadirpools', {})
create_resources(bacula::dir::pool, $baculadirpools)

$baculadirjobs=hiera_hash('baculadirjobs', {})
create_resources(bacula::dir::job, $baculadirjobs)

$baculadirjobtemplates=hiera_hash('baculadirjobtemplates', {})
create_resources(bacula::dir::jobtemplate, $baculadirjobtemplates)


#
# eyp-yum
#

$yumreposyncs=hiera_hash('yumreposyncs', {})
create_resources(yum::reposync, $yumreposyncs)

#
# eyp-rhn
#

$rhnrepos=hiera_hash('rhnrepos', {})
create_resources(rhn::repo, $rhnrepos)

#
# eyp-initscript
#

$initscripts=hiera_hash('initscripts', {})
create_resources(initscript::service, $initscripts)

#
# eyp-openscap
#

$openscapscannerxccdfs=hiera_hash('openscapscannerxccdfs', {})
create_resources(openscap::scanner::xccdf, $openscapscannerxccdfs)

$openscapscannerprofiles=hiera_hash('openscapscannerprofiles', {})
create_resources(openscap::scanner::profile, $openscapscannerprofiles)

#
# eyp-ossec
#

$ossecserversharedagentconfigs=hiera_hash('ossecserversharedagentconfigs', {})
create_resources(ossec::server::sharedagent::agentconfig, $ossecserversharedagentconfigs)

$ossecserversharedagentdirectories=hiera_hash('ossecserversharedagentdirectories', {})
create_resources(ossec::server::sharedagent::directories, $ossecserversharedagentdirectories)

$ossecserversharedagentignores=hiera_hash('ossecserversharedagentignores', {})
create_resources(ossec::server::sharedagent::ignore, $ossecserversharedagentignores)

$ossecserversharedagentlocalfiles=hiera_hash('ossecserversharedagentlocalfiles', {})
create_resources(ossec::server::sharedagent::localfile, $ossecserversharedagentlocalfiles)

$ossecserversharedagentrootchecks=hiera_hash('ossecserversharedagentrootchecks', {})
create_resources(ossec::server::sharedagent::rootcheck, $ossecserversharedagentrootchecks)


$ossecserverdirectories=hiera_hash('ossecserverdirectories', {})
create_resources(ossec::server::directories, $ossecserverdirectories)

$ossecserverignores=hiera_hash('ossecserverignores', {})
create_resources(ossec::server::ignore, $ossecserverignores)

create_resources(ossec::server::syslogoutput, hiera_hash('ossecserversyslogoutputs', {}))

#
# eyp-ldconfig
#

$ldconfigdirs=hiera_hash('ldconfigdirs', {})
create_resources(ldconfig::diradd, $ldconfigdirs)

#
# eyp-selinux
#

$selinuxbools=hiera_hash('selinuxbools', {})
create_resources(selinux::setbool, $selinuxbools)

#
# eyp-splunk
#

$splunkfwdmonitors=hiera_hash('splunkfwdmonitors', {})
create_resources(splunk::forwarder::monitor, $splunkfwdmonitors)

$splunkfwdtcpouts=hiera_hash('splunkfwdtcpouts', {})
create_resources(splunk::forwarder::outputs::tcpout, $splunkfwdtcpouts)

#
# eyp-atd
#

create_resources(atd::allowuser, hiera_hash('atdallowusers', {}))

#
# eyp-tuned
#

create_resources(tuned::profile, hiera_hash('tunedprofiles', {}))
create_resources(tuned::profile::disk, hiera_hash('tunedprofiledisks', {}))

#
# eyp-systemd
#

create_resources(systemd::service, hiera_hash('systemdservices', {}))

#
# eyp-sslh
#

create_resources(sslh::protocol, hiera_hash('sslhprotocols', {}))

#
# eyp-haproxy
#

create_resources(haproxy::balancer, hiera_hash('haproxybalancers', {}))
create_resources(haproxy::balancer::server, hiera_hash('haproxybalancerservers', {}))
create_resources(haproxy::stats, hiera_hash('haproxystats', {}))

#
# eyp-iptables
#

create_resources(iptables::rule, hiera_hash('iptablesrules', {}))

#
# classes
#
if versioncmp($::puppetversion, '4.0.0') >= 0
{
  lookup('classes', Array[String], 'deep').include
}
else
{
  hiera_include('classes')
}
''', file=write_to)

if __name__ == '__main__':
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = './siteppgen.config'
    generatesitepp(config_file=config_file)
