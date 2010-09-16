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
This script upload a file from web and publish it as 'study file' in S3
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, ssh_command, Timer

from balloon import amazon
from balloon.amazon import ssh as amazon_ssh

import os, os.path


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --remote-location='/mnt'"
an_usage_description += amazon_ssh.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

a_option_parser.add_option( "--source-location",
                            metavar = "< source location of the credendtials environemnt files >",
                            action = "store",
                            dest = "source_location",
                            help = "(\"%default\", by default)",
                            default = "/mnt" )
a_option_parser.add_option( "--remote-location",
                            metavar = "< destination of the credendtials environemnt files >",
                            action = "store",
                            dest = "remote_location",
                            help = "(\"%default\", by default)",
                            default = "/mnt" )
a_option_parser.add_option( "--aws-user-id",
                            metavar = "< AWS User ID >",
                            action = "store",
                            dest = "aws_user_id",
                            help = "(\"%default\", by default)",
                            default = os.getenv( "AWS_USER_ID" ) )
amazon_ssh.add_parser_options( a_option_parser )
amazon.add_parser_options( a_option_parser )
common.add_parser_options( a_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )
an_identity_file, a_host_port, a_login_name, a_host_name, a_command = amazon_ssh.extract_options( an_options )

a_source_location = os.path.abspath( an_options.source_location )
if not os.path.isdir( a_source_location ) :
    a_option_parser.error( "--script-location='%s' must be a folder" % a_source_location )
    pass

a_remote_location = os.path.abspath( an_options.remote_location )

AWS_USER_ID = an_options.aws_user_id
if AWS_USER_ID == None or AWS_USER_ID == "" :
    a_option_parser.error( "use '--aws-user-id' option to define proper AWS User ID" )
    pass

import sys
an_engine = sys.argv[ 0 ]
print_d( "%s --source-location='%s' --remote-location='%s' --identity-file='%s' --host-port=%d --login-name='%s' --host-name='%s'\n" % 
         ( an_engine, a_source_location, a_remote_location, an_identity_file, a_host_port, a_login_name, a_host_name ) )


#--------------------------------------------------------------------------------------
# Running actual functionality

import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
a_rsa_key = paramiko.RSAKey( filename = an_identity_file )

a_ssh_connect = lambda : a_ssh_client.connect( hostname = a_host_name, port = a_host_port, username = a_login_name, pkey = a_rsa_key )
amazon_ssh.wait_ssh( a_ssh_connect, a_ssh_client, a_command ) # Wait for execution of the first 'dummy' command

sh_command( "rsync --rsh='ssh -i %s' --rsync-path='sudo rsync' %s/{cert,pk}-*.pem %s@%s:%s" % 
            ( an_identity_file, a_source_location, a_login_name, a_host_name, a_remote_location ) )

a_remote_rcfile = os.path.join( a_remote_location, ".aws_credentialsrc")
ssh_command( a_ssh_client, 'echo "# AWS Credentials" > %s' % ( a_working_dir, a_remote_rcfile ) )
ssh_command( a_ssh_client, 'echo "export AWS_ACCESS_KEY_ID=%s" >> %s' % ( a_working_dir, AWS_ACCESS_KEY_ID, a_remote_rcfile ) )
ssh_command( a_ssh_client, 'echo "export AWS_SECRET_ACCESS_KEY=%s" >> %s' % ( a_working_dir, AWS_SECRET_ACCESS_KEY, a_remote_rcfile ) )
ssh_command( a_ssh_client, 'echo "export AWS_USER_ID=%s" >> %s' % ( a_working_dir, AWS_USER_ID, a_remote_rcfile ) )
ssh_command( a_ssh_client, 'echo "export EC2_PRIVATE_KEY=`%s/pk-*.pem`" >> %s' % ( a_working_dir, a_remote_location, a_remote_rcfile ) )
ssh_command( a_ssh_client, 'echo "export EC2_CERT=`%s/cert-*.pem`" >> %s' % ( a_working_dir, a_remote_location, a_remote_rcfile ) )

ssh_command( a_ssh_client, 'source %s && env | grep -E "AWS|EC2"' % ( a_remote_rcfile ) )


print_d( "\n--------------------------- Closing SSH connection ------------------------\n" )
a_ssh_client.close()

print an_identity_file
print a_host_name
print a_host_port


print_d( "\n-------------------------------------- OK ---------------------------------\n" )

