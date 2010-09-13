#!/usr/bin/env python

#--------------------------------------------------------------------------------------
## Copyright 2010 Alexey Petrov
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.


#--------------------------------------------------------------------------------------
"""
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, ssh_command, Timer

from balloon import amazon
from balloon.amazon import ec2 as amazon_ec2


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += " --identity-file='~/.ssh/tmpraDD2j.pem'"
an_usage_description += " --host-port=22"
an_usage_description += " --login-name='ubuntu'"
an_usage_description += " --host-name='ec2-184-73-11-20.compute-1.amazonaws.com'"
an_usage_description += amazon.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

a_option_parser.add_option( "--identity-file",
                            metavar = "< selects a file from which the identity (private key) for RSA or DSA authentication is read >",
                            action = "store",
                            dest = "identity_file",
                            default = None )
a_option_parser.add_option( "--login-name",
                            metavar = "< specifies the user to log in as on the remote machine >",
                            action = "store",
                            dest = "login_name",
                            help = "(\"%default\", by default)",
                            default = "ubuntu" )
a_option_parser.add_option( "--host-name",
                            metavar = "< instance public DNS >",
                            action = "store",
                            dest = "host_name",
                            default = None )
a_option_parser.add_option( "--host-port",
                            metavar = "< port to be used >",
                            type = "int",
                            action = "store",
                            dest = "host_port",
                            default = 22 )
a_option_parser.add_option( "--command",
                            metavar = "< command to be run on the remote machine >",
                            action = "store",
                            dest = "command",
                            help = "('%default', by default)",
                            default = "echo  > /dev/null" )
amazon.add_parser_options( a_option_parser )
common.add_parser_options( a_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

an_identity_file = an_options.identity_file
if an_identity_file == None :
    an_identity_file = raw_input()
    pass

import os.path
an_identity_file = os.path.expanduser( an_identity_file )
an_identity_file = os.path.abspath( an_identity_file )

a_login_name = an_options.login_name

a_host_name = an_options.host_name
if a_host_name == None :
    a_host_name = raw_input()
    pass

a_host_port = an_options.host_port
if a_host_port == None :
    a_host_port = int( raw_input() )
    pass

a_command = an_options.command

import sys
an_engine = sys.argv[ 0 ]

print_d( "%s --identity-file='%s' --host-port=%d --login-name='%s' --host-name='%s'\n" % 
         ( an_engine, an_identity_file, a_host_port, a_login_name, a_host_name ) )
print_d( 'ssh -i %s -p %d %s@%s\n' % ( an_identity_file, a_host_port, a_login_name, a_host_name ) )


#--------------------------------------------------------------------------------------
# Running actual functionality

import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
a_rsa_key = paramiko.RSAKey( filename = an_identity_file )

a_ssh_connect = lambda : a_ssh_client.connect( hostname = a_host_name, port = a_host_port, username = a_login_name, pkey = a_rsa_key )

amazon_ec2.wait_ssh( a_ssh_connect, a_ssh_client, a_command )

# print_d( "\n----------------------- Additional customization steps --------------------\n" )
# ssh_command( a_ssh_client, """sudo cat /etc/ssh/sshd_config""" )
# ssh_command( a_ssh_client, """sudo sh -c 'echo "\n    ClientAliveInterval 10\n    Port 22" >> /etc/ssh/ssh_config'""" )
# ssh_command( a_ssh_client, """sudo cat /etc/ssh/sshd_config""" )
# ssh_command( a_ssh_client, """sudo /etc/init.d/ssh restart""" )


print_d( "\n--------------------------- Closing SSH connection ------------------------\n" )
a_ssh_client.close()


print_d( "\n-------------------------------------- OK ---------------------------------\n" )

