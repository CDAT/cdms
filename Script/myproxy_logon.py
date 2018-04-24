#!/usr/bin/env python

import sys
import argparse
import getpass
import cdms2
import os

cert_file = os.path.join(os.environ["HOME"], ".esg", "credentials.pem")
parser = argparse.ArgumentParser(
    description='Retrieve ESGF Credentials via myproxy',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-s", "--host", "--server", "--pshost", dest="host", required=True,
                    help="The hostname of the MyProxy server to contact")
parser.add_argument("-p", "--psport", dest="port", default=7512, type=int,
                    help="The port of the MyProxy server to contact")
parser.add_argument("-l", "-u", "--user", "--username", dest="username",
                    help="The username with which the credential is stored on the MyProxy server")
parser.add_argument("-o", "--out", dest="outfile", default=cert_file,
                    help="The username with which the credential is stored on the MyProxy server")
parser.add_argument("-t", "--proxy-lifetime", dest="lifetime", default=43200,
                    help="The username with which the credential is stored on the MyProxy server")
parser.add_argument("-d", "--debug", dest="debug", default=0,
                    help="Debug mode: 1=print debug info ; 2=print as in (1), and dump data to myproxy.dump")
parser.add_argument("-L", "--lifetime", dest="lifetime", default=48, type=int,
                    help="lifetime")

options = parser.parse_args(sys.argv[1:])

debuglevel = options.debug

# process options
host = options.host
port = options.port
username = options.username
if not username:
    if sys.platform == 'win32':
        username = os.environ["USERNAME"]
    else:
        import pwd
        username = pwd.getpwuid(os.geteuid())[0]
lifetime = options.lifetime

outfile = options.outfile
if not outfile:
    if sys.platform == 'win32':
        outfile = 'proxy'
    elif sys.platform in ['linux2', 'darwin']:
        outfile = '/tmp/x509up_u%s' % (os.getuid())
elif outfile.lower() == "stdout":
    outfile = sys.stdout

# Get MyProxy password
passphrase = getpass.getpass()
# Retrieve proxy cert
ret = cdms2.myproxy_logon.myproxy_logon(
    host, username, passphrase, outfile, lifetime=lifetime, port=port)
print "A proxy has been received for user %s in %s." % (username, outfile)
