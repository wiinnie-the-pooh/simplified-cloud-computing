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
from balloon.common import print_d, print_e, sh_command, ssh_command

import balloon.amazon as amazon

import sys, os, os.path, uuid


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
common.add_parser_options( a_option_parser )

amazon.add_parser_options( a_option_parser )
    

#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


#---------------------------------------------------------------------------
import logging
logging.basicConfig( filename = "boto.log", level = logging.DEBUG )

import boto
an_ec2_conn = boto.connect_ec2()
print_d( '%r\n' % an_ec2_conn )

an_images = an_ec2_conn.get_all_images( image_ids = "ami-2d4aa444" )
an_image = an_images[ 0 ]
print_d( '%s\n' % an_image.location )

# Amazon EC2 does not accept UUID based names
# import uuid
# a_key_pair_name = 'id_rsa_%s' % str( uuid.uuid4() )

import tempfile
an_unique_file = tempfile.mkstemp()[ 1 ]
an_unique_name = os.path.basename( an_unique_file )
os.remove( an_unique_file )
print an_unique_name

a_key_pair_name = an_unique_name
a_key_pair = an_ec2_conn.create_key_pair( a_key_pair_name )

a_key_pair_dir = os.path.expanduser( "~/.ssh")
a_key_pair.save( a_key_pair_dir )
a_key_pair_file = os.path.join( a_key_pair_dir, a_key_pair.name ) + os.path.extsep + "pem"
print a_key_pair_file

import stat
os.chmod( a_key_pair_file, stat.S_IRUSR )

a_security_group = an_ec2_conn.create_security_group( an_unique_name, 'temporaly generated' )
a_security_group.authorize( 'tcp', 80, 80, '0.0.0.0/0' )
a_security_group.authorize( 'tcp', 22, 22, '0.0.0.0/0' )

a_reservation = an_image.run( instance_type = 'm1.small', min_count = 1, max_count = 1, key_name = a_key_pair_name, security_groups = [ a_security_group.name ] )
an_instance = a_reservation.instances[ 0 ]
print_d( '%s ' % an_instance.update() )

while True :
    try :
        if an_instance.update() == 'running' :
            break
        print_d( '.' )
    except :
        continue
    pass

print_d( ' %s\n' % an_instance.update() )
print_d( '%s\n' % an_instance.dns_name )

import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
a_rsa_key = paramiko.RSAKey( filename = a_key_pair_file )

while True :
    try :
        a_username = 'ubuntu'
        a_ssh_client.connect( hostname = an_instance.dns_name, port = 22, username = a_username, pkey = a_rsa_key )
        ssh_command( a_ssh_client, 'echo  > /dev/null' )
        break
    except :
        continue
    pass

ssh_command( a_ssh_client, 'ls -l /' )

print_d( 'ssh -i %s %s@%s\n' ( a_key_pair_file, a_username, an_instance.dns_name ))


#---------------------------------------------------------------------------
a_ssh_client.close()

# an_ec2_conn.delete_security_group( a_security_group.name )
# an_ec2_conn.delete_key_pair( a_key_pair_name )
# os.remove( a_key_pair_file )
# a_reservation.stop_all()


#---------------------------------------------------------------------------
print_d( 'OK\n' )


#--------------------------------------------------------------------------------------
