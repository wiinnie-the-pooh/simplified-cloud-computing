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

import balloon.amazon as amazon

import sys, os, os.path, uuid


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --image-id='ami-2d4aa444' --image-location='us-east-1' --instance-type='m1.small' --user-name='ubuntu'"
# an_usage_description = "%prog --image-id='ami-fd4aa494' --image-location='us-east-1' --instance-type='m1.large' --user-name='ubuntu'"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--image-id",
                            metavar = "< Amazon EC2 AMI ID >",
                            action = "store",
                            dest = "image_id",
                            help = "(\"%default\", by default)",
                            default = "ami-2d4aa444" )

a_option_parser.add_option( "--image-location",
                            metavar = "< location of the AMI >",
                            action = "store",
                            dest = "image_location",
                            help = "(\"%default\", by default)",
                            default = "us-east-1" )

a_option_parser.add_option( "--instance-type",
                            metavar = "< type of the instance in terms of EC2 >",
                            action = "store",
                            dest = "instance_type",
                            help = "(\"%default\", by default)",
                            default = "m1.small" )

a_option_parser.add_option( "--user-name",
                            metavar = "< SSH connection user name >",
                            action = "store",
                            dest = "user_name",
                            help = "(\"%default\", by default)",
                            default = "ubuntu" )

common.add_parser_options( a_option_parser )

amazon.add_parser_options( a_option_parser )
    
print_d( "\n---------------------------------------------------------------------------\n" )
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

an_image_ids = an_options.image_id
an_image_location = an_options.image_location
an_instance_type = an_options.instance_type
a_username = an_options.user_name

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


print_d( "\n-------------------------- Defining image location ------------------------\n" )
# Instanciating node in cloud
an_instance_reservation_time = Timer()

# Establish an connection with EC2
import boto.ec2
a_regions = boto.ec2.regions()
print_d( 'a_regions = %r\n' % a_regions )

an_image_region = None
for a_region in a_regions :
    if a_region.name == an_image_location :
        an_image_region = a_region
        pass
    pass

if an_image_region == None :
    print_e( "There no region with such location - '%s'\n" % an_image_region )
    pass

print_d( 'an_image_region = < %r >\n' % an_image_region )

an_ec2_conn = an_image_region.connect( aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY )
print_d( 'an_ec2_conn = < %r >\n' % an_ec2_conn )

an_images = an_ec2_conn.get_all_images( image_ids = an_image_ids )
an_image = an_images[ 0 ]
print_d( 'an_image = < %s >\n' % an_image )


print_d( "\n---------------- Creating unique key-pair and security group --------------\n" )
import tempfile
an_unique_file = tempfile.mkstemp()[ 1 ]
an_unique_name = os.path.basename( an_unique_file )
os.remove( an_unique_file )
print_d( "an_unique_name = '%s'\n" % an_unique_name )

# Asking EC2 to generate a new ssh "key pair"
a_key_pair_name = an_unique_name
a_key_pair = an_ec2_conn.create_key_pair( a_key_pair_name )

# Saving the generated ssh "key pair" locally
a_key_pair_dir = os.path.expanduser( "~/.ssh")
a_key_pair.save( a_key_pair_dir )
a_key_pair_file = os.path.join( a_key_pair_dir, a_key_pair.name ) + os.path.extsep + "pem"
print_d( "a_key_pair_file = '%s'\n" % a_key_pair_file )

import stat
os.chmod( a_key_pair_file, stat.S_IRUSR )

# Asking EC2 to generate a new "sequirity group" & apply corresponding firewall permissions
a_security_group = an_ec2_conn.create_security_group( an_unique_name, 'temporaly generated' )
a_security_group.authorize( 'tcp', 80, 80, '0.0.0.0/0' )
a_security_group.authorize( 'tcp', 22, 22, '0.0.0.0/0' )


print_d( "\n-------------------------- Actual running the image -----------------------\n" )
# Creating a EC2 "reservation" with all the parameters mentioned above
a_reservation = an_image.run( instance_type = an_instance_type, min_count = 1, max_count = 1, 
                              key_name = a_key_pair_name, security_groups = [ a_security_group.name ] )
an_instance = a_reservation.instances[ 0 ]
print_d( 'a_reservation.instances = %s\n' % a_reservation.instances )


print_d( "\n-------------- Instantiating ssh connection with root access --------------\n" )
# Instantiating ssh connection with root access
import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
a_rsa_key = paramiko.RSAKey( filename = a_key_pair_file )

a_ssh_connect = lambda : a_ssh_client.connect( hostname = an_instance.dns_name, port = 22, username = a_username, pkey = a_rsa_key )

# Making sure that corresponding instances are ready to use
from balloon.amazon import wait_activation
wait_activation( an_instance, a_ssh_connect, a_ssh_client )
print_d( 'ssh -i %s %s@%s\n' % ( a_key_pair_file, a_username, an_instance.dns_name ) )

print_d( "an_instance_reservation_time = %s, sec\n" % an_instance_reservation_time )


# print_d( "\n----------------------- Additional customization steps --------------------\n" )
# ssh_command( a_ssh_client, """sudo cat /etc/ssh/ssh_config""" )
# ssh_command( a_ssh_client, """sudo sh -c 'echo "\n    ClientAliveInterval 10\n    Port 22" >> /etc/ssh/ssh_config'""" )
# ssh_command( a_ssh_client, """sudo cat /etc/ssh/ssh_config""" )
# ssh_command( a_ssh_client, """sudo /etc/init.d/ssh restart""" )


print_d( "\n--------------------------- Closing SSH connection ------------------------\n" )
a_ssh_client.close()


print_d( "\n-------------------------------------- OK ---------------------------------\n" )

