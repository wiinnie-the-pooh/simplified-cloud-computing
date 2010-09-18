
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
from balloon.common import print_e, print_d, ssh_command, Timer, wait_ssh


#--------------------------------------------------------------------------------------
def add_usage_description() :
    return " [ --password='P@ssw0rd' | --identity-file='~/.ssh/tmpraDD2j.pem' ] --host-port=22 --login-name='ubuntu' --host-name='ec2-184-73-11-20.compute-1.amazonaws.com'"


#--------------------------------------------------------------------------------------
def add_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--password",
                                  metavar = "< password for the given host and login name >",
                                  action = "store",
                                  dest = "password",
                                  default = "" )
    the_option_parser.add_option( "--identity-file",
                                  metavar = "< selects a file from which the identity (private key) for RSA or DSA authentication is read >",
                                  action = "store",
                                  dest = "identity_file",
                                  default = "" )
    the_option_parser.add_option( "--host-port",
                                  metavar = "< port to be used >",
                                  type = "int",
                                  action = "store",
                                  dest = "host_port",
                                  default = None )
    the_option_parser.add_option( "--login-name",
                                  metavar = "< specifies the user to log in as on the remote machine >",
                                  action = "store",
                                  dest = "login_name",
                                  help = "(\"%default\", by default)",
                                  default = None )
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
def print_ssh( the_password, the_identity_file, the_host_port, the_login_name, the_host_name )
    if a_password != "" :
        print_d( 'sshpass -p %s ssh -p %d %s@%s\n' % ( the_password, the_host_port, the_login_name, the_host_name ) )
    else :
        print_d( 'ssh -i %s -p %d %s@%s\n' % ( the_identity_file, the_host_port, the_login_name, the_host_name ) )
        pass
    pass


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    a_password = the_options.password
    if a_password == "" :
        a_password = raw_input()
        pass
    the_options.password = a_password

    an_identity_file = the_options.identity_file
    if an_identity_file == "" :
        an_identity_file = raw_input()
        pass
    if an_identity_file != "" :
        import os.path
        an_identity_file = os.path.expanduser( an_identity_file )
        an_identity_file = os.path.abspath( an_identity_file )
        pass
    the_options.identity_file = an_identity_file

    a_host_port = the_options.host_port
    if a_host_port == None :
        a_host_port = int( raw_input() )
        pass
    the_options.host_port = a_host_port

    a_login_name = the_options.login_name
    if a_login_name == None :
        a_login_name = raw_input()
        pass
    the_options.login_name = a_login_name

    a_host_name = the_options.host_name
    if a_host_name == None :
        a_host_name = raw_input()
        pass
    the_options.host_name = a_host_name

    a_command = the_options.command

    print_ssh( the_options.password, the_options.identity_file, the_options.host_port, the_options.login_name, the_options.host_name )

    return a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command


#--------------------------------------------------------------------------------------
def print_options( the_options ) :
    print_ssh( the_options.password, the_options.identity_file, the_options.host_port, the_options.login_name, the_options.host_name )

    print the_options.password
    print the_options.identity_file
    print the_options.host_port
    print the_options.login_name
    print the_options.host_name

    pass

#--------------------------------------------------------------------------------------