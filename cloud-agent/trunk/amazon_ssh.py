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

an_usage_description = "%prog [ --script-file='./config_sshd.sh' ] [ --sequence-file='./config_sshd.sh' ]"
an_usage_description += amazon_ssh.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

a_option_parser.add_option( "--script-file",
                            metavar = "< script to be executed on the remote host >",
                            action = "store",
                            dest = "script_file",
                            default = None )
a_option_parser.add_option( "--sequence-file",
                            metavar = "< file with sequence of commands to be executed >",
                            action = "store",
                            dest = "sequence_file",
                            default = None )
amazon_ssh.add_parser_options( a_option_parser )
common.add_parser_options( a_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
an_identity_file, a_host_port, a_login_name, a_host_name, a_command = amazon_ssh.extract_options( an_options )

import sys
an_engine = sys.argv[ 0 ]
a_call = "%s --identity-file='%s' --host-port=%d --login-name='%s' --host-name='%s' --command='%s'" % \
    ( an_engine, an_identity_file, a_host_port, a_login_name, a_host_name, a_command )

import os.path

a_script_file = an_options.script_file
if a_script_file != None :
    a_script_file = os.path.abspath( a_script_file )
    if not os.path.isfile( a_script_file ) :
        a_option_parser.error( "--script-file='%s' must be a file" % a_script_file )
        pass
    a_call += " --script-file='%s'" % a_script_file
    pass

a_sequence_file = an_options.sequence_file
if a_sequence_file != None :
    a_sequence_file = os.path.abspath( a_sequence_file )
    if not os.path.isfile( a_sequence_file ) :
        a_option_parser.error( "--sequence-file='%s' must be a file" % a_sequence_file )
        pass
    a_call += " --sequence-file='%s'" % a_sequence_file
    pass

print_d( a_call + '\n' )


#--------------------------------------------------------------------------------------
# Running actual functionality

import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
a_rsa_key = paramiko.RSAKey( filename = an_identity_file )

a_ssh_connect = lambda : a_ssh_client.connect( hostname = a_host_name, port = a_host_port, username = a_login_name, pkey = a_rsa_key )
amazon_ssh.wait_ssh( a_ssh_connect, a_ssh_client, a_command ) 

if a_script_file != None :
    a_working_dir = ssh_command( a_ssh_client, 'python -c "import os, os.path, tempfile; print tempfile.mkdtemp()"' )[ 0 ][ : -1 ]
    a_target_script = os.path.join( a_working_dir, os.path.basename( a_script_file ) )

    a_sftp_client = a_ssh_client.open_sftp() # Instantiating a sftp client
    a_sftp_client.put( a_script_file, a_target_script )
    
    ssh_command( a_ssh_client, 'chmod 755 "%s"' % a_target_script )
    ssh_command( a_ssh_client, 'sudo "%s"' % a_target_script )
    
    ssh_command( a_ssh_client, """python -c 'import shutil; shutil.rmtree( "%s" )'""" % a_working_dir )
    pass


if a_sequence_file != None :
    a_file = open( a_sequence_file )
    for a_line in a_file.readlines() :
        if a_line[ 0 ] == "#" or a_line[ 0 ] == "\n" :
            continue
        ssh_command( a_ssh_client, 'sudo %s' % a_line[ : -1 ] )
        pass
    a_file.close()
    pass


print_d( "\n--------------------------- Closing SSH connection ------------------------\n" )
a_ssh_client.close()

print an_identity_file
print a_host_name
print a_host_port


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
