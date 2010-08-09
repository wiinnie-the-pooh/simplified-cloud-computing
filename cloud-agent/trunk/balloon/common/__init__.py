

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
import os, sys


#--------------------------------------------------------------------------------------
ENABLE_DEBUG = None


#--------------------------------------------------------------------------------------
def add_usage_description() :
    return " --debug"


#--------------------------------------------------------------------------------------
def add_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--debug",
                                  action = "store_true",
                                  dest = "enable_debug",
                                  help = "print debug information",
                                  default = True )
    pass


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    global ENABLE_DEBUG

    ENABLE_DEBUG = the_options.enable_debug

    return ENABLE_DEBUG


#---------------------------------------------------------------------------
def print_d( the_message ) :
    if ENABLE_DEBUG : 
        sys.stderr.write( the_message )
        pass
    
    pass


#---------------------------------------------------------------------------
def print_e( the_message ) :
    sys.stderr.write( the_message )
    
    os._exit( os.EX_USAGE )
    pass


#---------------------------------------------------------------------------
def sh_command( the_command ) :
    print_d( "(%s)\n" % the_command )
    
    if os.system( the_command ) != 0 :
        print_e( "Can not execute command %s\n" % the_command )
        pass
    
    pass


#---------------------------------------------------------------------------
def ssh_command( the_ssh_client, the_command ) :
    print_d( "[%s]\n" % the_command )
    
    stdin, stdout, stderr = the_ssh_client.exec_command( the_command )
    
    for a_line in stderr.readlines() : print_d( "\t%s" % a_line )
    for a_line in stdout.readlines() : print_d( "\t%s" % a_line )

    pass


#--------------------------------------------------------------------------------------
