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
from balloon.amazon import ssh as amazon_ssh


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += amazon_ssh.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

amazon_ssh.add_parser_options( a_option_parser )
common.add_parser_options( a_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
an_identity_file, a_host_port, a_login_name, a_host_name, a_command = amazon_ssh.extract_options( an_options )


#--------------------------------------------------------------------------------------
# Running actual functionality
import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
a_rsa_key = paramiko.RSAKey( filename = an_identity_file )

a_ssh_connect = lambda : a_ssh_client.connect( hostname = a_host_name, port = a_host_port, username = a_login_name, pkey = a_rsa_key )
amazon_ssh.wait_ssh( a_ssh_connect, a_ssh_client, a_command )

ssh_command( a_ssh_client, """sudo cat /etc/ssh/sshd_config""" )
ssh_command( a_ssh_client, """sudo sh -c 'echo "\nClientAliveInterval 3600" >> /etc/ssh/sshd_config'""" )
ssh_command( a_ssh_client, """sudo perl -p -i -e 's%^LoginGraceTime%#LoginGraceTime%g' /etc/ssh/sshd_config""" )
ssh_command( a_ssh_client, """sudo cat /etc/ssh/sshd_config""" )
ssh_command( a_ssh_client, """sudo /etc/init.d/ssh restart""" )


print_d( "\n--------------------------- Closing SSH connection ------------------------\n" )
a_ssh_client.close()

print an_identity_file
print a_host_name
print a_host_port


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
