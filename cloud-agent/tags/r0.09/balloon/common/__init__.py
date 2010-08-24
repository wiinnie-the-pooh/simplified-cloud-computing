

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
from subprocess import *


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
PRINTING_DEPTH = 0

class init_printing :
    "To provide hierarchical 'pretty' printing"
    def __init__( self ) :
        global PRINTING_DEPTH

        # PRINTING_DEPTH += 1

        pass

    def __del__( self ) :
        global PRINTING_DEPTH

        # PRINTING_DEPTH -= 1

        pass

    pass

def get_preffix( the_preffix, the_printing_depth ) :
    "Calaculate a preffix identation according to the current printing stack depth"
    a_preffix = ""
    for id in range( the_printing_depth ) :
        a_preffix += the_preffix
        pass

    return a_preffix


#---------------------------------------------------------------------------
def print_d( the_message, the_printing_depth = 0 ) :
    "Optional printing of debug messages"
    if ENABLE_DEBUG : 
        sys.stderr.write( get_preffix( "    ", the_printing_depth ) + the_message )
        pass
    
    pass


#---------------------------------------------------------------------------
def print_i( the_message, the_printing_depth = 0 ) :
    "Optional printing of debug messages"

    print_d( "\n" )

    print_d( the_message, the_printing_depth )

    pass


#---------------------------------------------------------------------------
def print_e( the_message ) :
    "Printing of error message and quit"
    print_d( "\n---------------------------------------------------------------------------\n" )

    sys.stderr.write( "Error : " + the_message )
    
    print_d( "\n---------------------------------------------------------------------------\n" )
    print_d( 'KO\n' )

    os._exit( os.EX_USAGE )
    pass


#---------------------------------------------------------------------------
def sh_command( the_command, the_printing_depth = 0 ) :
    "Execution of shell command"
    print_d( "(%s)\n" % the_command, the_printing_depth )
    
    a_pipe = Popen( the_command, stdout = PIPE, stderr = PIPE, shell = True )

    a_return_code = os.waitpid( a_pipe.pid, 0 )[ 1 ]

    for a_line in a_pipe.stderr.readlines() : print_d( "\t%s" % a_line )
    for a_line in a_pipe.stdout.readlines() : print_d( "\t%s" % a_line )

    if a_return_code != 0 :
        os._exit( os.EX_USAGE )
        pass
    
    pass


#---------------------------------------------------------------------------
def ssh_command( the_ssh_client, the_command ) :
    "Execution of secure shell command"
    print_d( "[%s]\n" % the_command )
    
    stdin, stdout, stderr = the_ssh_client.exec_command( the_command )
    
    for a_line in stderr.readlines() : print_d( "\t%s" % a_line )
    for a_line in stdout.readlines() : print_d( "\t%s" % a_line )

    pass


#---------------------------------------------------------------------------
def generate_queue_name( the_container_name, the_queue_suffix ) :
    "Generating composite queue name"
    
    return '%s___%s' % ( the_container_name, the_queue_suffix )


#---------------------------------------------------------------------------
def generate_initial_queue_name( the_container_name ) :
    "Defining the initial queue name"
    a_queue_suffix = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    
    return generate_queue_name( the_container_name, a_queue_suffix )


#---------------------------------------------------------------------------
def generate_message_body( the_file_name, the_next_queue_suffix ) :
    "Generating specially formatted message"
    
    return '%s:%s' % ( the_file_name, the_next_queue_suffix )


#---------------------------------------------------------------------------
def generate_final_message_body( the_container_name ) :
    "Defining the final message"
    
    return generate_message_body( the_container_name, '*' )


#--------------------------------------------------------------------------------------
def push_message( the_sqs_queue, the_string ) :
    "Publishing message through Amazon SQS"
    from boto.sqs.message import Message

    a_message = Message()
    a_message.set_body( the_string )

    return the_sqs_queue.write( a_message )


#--------------------------------------------------------------------------------------
def get_message( the_sqs_conn, the_queue_name ) :
    "Receiving and parsing the incoming Amazon SQS message"

    # Get the 'queue' first
    a_sqs_queue = None
    while True :
        a_sqs_queue = the_sqs_conn.get_queue( the_queue_name )
        if a_sqs_queue != None :
            break
        pass

    # Now, get message
    a_message_body = ''
    while True :
        a_message = a_sqs_queue.read()
        if a_message != None :
            a_message_body = a_message.get_body()
            break
        pass

    a_sqs_queue.delete()

    a_data_name, a_next_queue_suffix = a_message_body.split( ':' )

    an_is_final = False
    if a_next_queue_suffix == '*':
        an_is_final = True
        pass

    return an_is_final, a_data_name, a_next_queue_suffix


#--------------------------------------------------------------------------------------
class Timer :
    def __init__( self ) :
        import time
        self.initial = time.time()
        pass

    def __str__( self ) :
        import time
        return str( "%f" % ( time.time() - self.initial ))

    pass


#--------------------------------------------------------------------------------------
