
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
from balloon.common import print_e, print_d, ssh_command, Timer


#--------------------------------------------------------------------------------------
def add_usage_description() :
    return " --identity-file='~/.ssh/tmpraDD2j.pem' --host-port=22 --login-name='ubuntu' --host-name='ec2-184-73-11-20.compute-1.amazonaws.com'"


#--------------------------------------------------------------------------------------
def add_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--identity-file",
                                  metavar = "< selects a file from which the identity (private key) for RSA or DSA authentication is read >",
                                  action = "store",
                                  dest = "identity_file",
                                  default = None )
    the_option_parser.add_option( "--host-port",
                                  metavar = "< port to be used >",
                                  type = "int",
                                  action = "store",
                                  dest = "host_port",
                                  default = 22 )
    the_option_parser.add_option( "--login-name",
                                  metavar = "< specifies the user to log in as on the remote machine >",
                                  action = "store",
                                  dest = "login_name",
                                  help = "(\"%default\", by default)",
                                  default = "ubuntu" )
    the_option_parser.add_option( "--host-name",
                                  metavar = "< instance public DNS >",
                                  action = "store",
                                  dest = "host_name",
                                  default = None )
    the_option_parser.add_option( "--command",
                                  metavar = "< command to be run on the remote machine >",
                                  action = "store",
                                  dest = "command",
                                  help = "('%default', by default)",
                                  default = "echo  > /dev/null" )
    return the_option_parser


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    an_identity_file = the_options.identity_file
    if an_identity_file == None :
        an_identity_file = raw_input()
        pass

    import os.path
    an_identity_file = os.path.expanduser( an_identity_file )
    an_identity_file = os.path.abspath( an_identity_file )

    a_host_port = the_options.host_port
    if a_host_port == None :
        a_host_port = int( raw_input() )
        pass

    a_login_name = the_options.login_name

    a_host_name = the_options.host_name
    if a_host_name == None :
        a_host_name = raw_input()
        pass

    a_command = the_options.command

    print_d( 'ssh -i %s -p %d %s@%s\n' % ( an_identity_file, a_host_port, a_login_name, a_host_name ) )

    return an_identity_file, a_host_port, a_login_name, a_host_name, a_command


#--------------------------------------------------------------------------------------
def wait_ssh( the_ssh_connect, the_ssh_client, the_command ) :
    print_d( "ssh'ing " )
    while True :
        try :
            print_d( '.' )
            the_ssh_connect()
            ssh_command( the_ssh_client, the_command )
            break
        except :
            # import sys, traceback
            # traceback.print_exc( file = sys.stderr )
            continue
        pass

    pass


#--------------------------------------------------------------------------------------
