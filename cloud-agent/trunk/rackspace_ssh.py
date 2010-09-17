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
from balloon.common import print_d, print_e, sh_command, ssh_command, wait_ssh, Timer

import balloon.rackspace as rackspace


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += " [ --script-file='./remote_adjust_profile.sh|./remote_update_sources-list.sh' ] [ --sequence-file='./remote_sshd-config.sh' ]"
an_usage_description += " --password='P@ssw0rd' --host-port=22 --login-name='root' --host-name='173.203.218.253'"
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

an_option_parser.add_option( "--password",
                             metavar = "< password for the given host and user name >",
                             action = "store",
                             dest = "password",
                             default = None )
an_option_parser.add_option( "--host-port",
                             metavar = "< port to be used >",
                             type = "int",
                             action = "store",
                             dest = "host_port",
                             default = 22 )
an_option_parser.add_option( "--login-name",
                             metavar = "< specifies the user to log in as on the remote machine >",
                             action = "store",
                             dest = "login_name",
                             help = "(\"%default\", by default)",
                             default = "root" )
an_option_parser.add_option( "--host-name",
                             metavar = "< instance public DNS >",
                             action = "store",
                             dest = "host_name",
                             default = None )
an_option_parser.add_option( "--command",
                             metavar = "< command to be run on the remote machine >",
                             action = "store",
                             dest = "command",
                             help = "('%default', by default)",
                             default = "echo  > /dev/null" )
an_option_parser.add_option( "--script-file",
                             metavar = "< script (or list of scripts separated by '|') to be executed on the remote host >",
                             action = "store",
                             dest = "script_file",
                             default = None )
an_option_parser.add_option( "--script-args",
                             metavar = "< arguments (or list of arguments separated by '|') for the remote script execution >",
                             action = "store",
                             dest = "script_args",
                             default = "" )
an_option_parser.add_option( "--sequence-file",
                             metavar = "< file with sequence of commands to be executed >",
                             action = "store",
                             dest = "sequence_file",
                             default = None )
amazon_ssh.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )

a_password = an_options.password
if a_password == None :
    a_password = raw_input()
    pass

a_host_port = an_options.host_port
if a_host_port == None :
    a_host_port = int( raw_input() )
    pass

a_login_name = an_options.login_name

a_host_name = an_options.host_name
if a_host_name == None :
    a_host_name = raw_input()
    pass

a_command = an_options.command

print_d( 'sshpass -p %s ssh -p %d %s@%s\n' % ( a_password, a_host_port, a_login_name, a_host_name ) )

import sys
an_engine = sys.argv[ 0 ]
a_call = "%s --password='%s' --host-port=%d --login-name='%s' --host-name='%s' --command='%s'" % \
    ( an_engine, a_password, a_host_port, a_login_name, a_host_name, a_command )

import os.path

an_args = None
a_scripts = None
a_script_file = an_options.script_file
if a_script_file != None :
    # First, check that all appointed scripts exists and regular files
    a_scripts = a_script_file.split( '|' )
    for a_script in a_scripts :
        if not os.path.isfile( a_script ) :
            an_option_parser.error( "--script-file='%s' must be a file" % a_script )
            pass
        pass

    # Next, check wether number of 'scripts' match number of script's args
    a_script_args = an_options.script_args
    if a_script_args != "" :
        an_args = a_script_args.split( '|' )
        if len( an_args ) != len( a_scripts ) :
            an_option_parser.error( "number of items in --script-file='%s'"
                                   " must the same or zero as for --script-args='%s' " 
                                   % ( a_script_files, a_script_args ) )
            pass
    else :
        an_args = [ "" for a_script in a_scripts ]
        pass
    
    a_call += " --script-file='%s'" % a_script_file
    if a_script_args != "" :
        a_call += " --script-args='%s'" % a_script_args
        pass
    pass

a_sequence_file = an_options.sequence_file
if a_sequence_file != None :
    a_sequence_file = os.path.abspath( a_sequence_file )
    if not os.path.isfile( a_sequence_file ) :
        an_option_parser.error( "--sequence-file='%s' must be a file" % a_sequence_file )
        pass
    a_call += " --sequence-file='%s'" % a_sequence_file
    pass

print_d( a_call + '\n' )


#--------------------------------------------------------------------------------------
# Running actual functionality

import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

a_ssh_connect = lambda : a_ssh_client.connect( hostname = a_host_name, port = a_host_port, username = a_login_name, password = a_password )
amazon_ssh.wait_ssh( a_ssh_connect, a_ssh_client, a_command ) 

if a_scripts != None :
    for an_id in range( len( a_scripts ) ) :
        a_script_file = a_scripts[ an_id ]
        a_script_args = an_args[ an_id ]
        
        a_working_dir = ssh_command( a_ssh_client, 'python -c "import os, os.path, tempfile; print tempfile.mkdtemp()"' )[ 0 ][ : -1 ]
        a_target_script = os.path.join( a_working_dir, os.path.basename( a_script_file ) )
        
        a_sftp_client = a_ssh_client.open_sftp() # Instantiating a sftp client
        a_sftp_client.put( a_script_file, a_target_script )
        
        ssh_command( a_ssh_client, 'chmod 755 "%s"' % a_target_script )
        ssh_command( a_ssh_client, 'sudo "%s" %s' % ( a_target_script, a_script_args ) )

        ssh_command( a_ssh_client, """python -c 'import shutil; shutil.rmtree( "%s" )'""" % a_working_dir )
        pass
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

print a_password
print a_host_name
print a_host_port


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
