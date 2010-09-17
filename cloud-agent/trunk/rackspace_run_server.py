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
from balloon.common import print_d, print_e, sh_command, ssh_command, wait_ssh, Timer

import balloon.rackspace as rackspace

import sys, os, os.path, uuid


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += common.add_usage_description()
an_usage_description += rackspace.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

rackspace.add_parser_options( a_option_parser )
common.add_parser_options( a_option_parser )
    

#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
RACKSPACE_USER, RACKSPACE_KEY = rackspace.extract_options( an_options )


print_d( "\n----------------------- Instanciating node in cloud -----------------------\n" )
# Instanciating node in cloud
an_instance_reservation_time = Timer()

from libcloud.types import Provider 
from libcloud.providers import get_driver 

Driver = get_driver( Provider.RACKSPACE ) 
a_libcloud_conn = Driver( RACKSPACE_USER, RACKSPACE_KEY ) 
print_d( "a_libcloud_conn = %r\n" % a_libcloud_conn )

an_images = a_libcloud_conn.list_images() 
print_d( "an_images = %r\n" % an_images )

a_sizes = a_libcloud_conn.list_sizes() 
print_d( "a_sizes = %r\n" % a_sizes )

a_node_name = str( uuid.uuid4() )
print_d( "an_images = %r\n" % an_images )
a_node = a_libcloud_conn.create_node( name = a_node_name, image = an_images[ 9 ] , size = a_sizes[ 0 ] ) 
print_d( "a_node = %r\n" % a_node )

print_d( "an_instance_reservation_time = %s, sec\n" % an_instance_reservation_time )


print_d( "\n--------------------------------- ssh'ing ---------------------------------\n" )
a_task_execution_time = Timer()

# Instantiating ssh connection with root access
import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

a_username = 'root'
a_password = a_node.extra.get( 'password' )
print_d( 'sshpass -p %s ssh %s@%s\n' % ( a_password, a_username, a_node.public_ip[ 0 ] ) )

a_ssh_connect = lambda : a_ssh_client.connect( hostname = a_node.public_ip[ 0 ], port = 22, username = a_username, password = a_password )
wait_ssh( a_ssh_connect, a_ssh_client, 'echo  > /dev/null' ) # Wait for execution of the first 'dummy' command

print_d( "a_task_execution_time = %s, sec\n" % a_task_execution_time )


print_d( "\n-------------------------- Closing connection -----------------------------\n" )
a_ssh_client.close()


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
