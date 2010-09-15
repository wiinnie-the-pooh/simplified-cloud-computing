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
This script helps to perform a command into remote cloud instance through ssh protocol,
  where the main problem is to establish proper connection 
  (server inocation & ssh timeout problems)
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, ssh_command, Timer

from balloon import amazon
from balloon.amazon import ssh as amazon_ssh


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog [ --file='./config_sshd.sh' ]"
an_usage_description += amazon_ssh.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

a_option_parser.add_option( "--file",
                            metavar = "< command sequence file to be executed >",
                            action = "store",
                            dest = "file",
                            default = None )
amazon_ssh.add_parser_options( a_option_parser )
common.add_parser_options( a_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
an_identity_file, a_host_port, a_login_name, a_host_name, a_command = amazon_ssh.extract_options( an_options )

import os.path
a_file = an_options.file
if a_file != None :
    a_file = os.path.abspath( an_options.file )
    if not os.path.isfile( a_file ) :
        a_option_parser.error( "--file='%s' must be a file" % a_file )
        print_e( "The task 'control' should contain 'launch' start-up script\n" )
    pass


#--------------------------------------------------------------------------------------
# Running actual functionality

import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
a_rsa_key = paramiko.RSAKey( filename = an_identity_file )

a_ssh_connect = lambda : a_ssh_client.connect( hostname = a_host_name, port = a_host_port, username = a_login_name, pkey = a_rsa_key )
amazon_ssh.wait_ssh( a_ssh_connect, a_ssh_client, a_command ) 

if a_file != None :
    a_working_dir = ssh_command( a_ssh_client, 'python -c "import os, os.path, tempfile; print tempfile.mkdtemp()"' )[ 0 ][ : -1 ]
    a_target_file = os.path.join( a_working_dir, os.path.basename( a_file ) )

    a_sftp_client = a_ssh_client.open_sftp() # Instantiating a sftp client
    a_sftp_client.put( a_file, a_target_file )
    
    ssh_command( a_ssh_client, 'chmod 755 "%s"' % a_target_file )
    ssh_command( a_ssh_client, '"%s"' % a_target_file )
    
    ssh_command( a_ssh_client, """python -c 'import shutil; shutil.rmtree( "%s" )'""" % a_working_dir )
    pass


print_d( "\n--------------------------- Closing SSH connection ------------------------\n" )
a_ssh_client.close()

print an_identity_file
print a_host_name
print a_host_port


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
