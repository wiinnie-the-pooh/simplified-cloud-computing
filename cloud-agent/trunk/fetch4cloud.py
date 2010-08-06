#!/usr/bin/env python


#--------------------------------------------------------------------------------------
"""
This script is responsible for fetching of the task resulting data from the cloud
"""


#--------------------------------------------------------------------------------------
import os


#--------------------------------------------------------------------------------------
def get_message( the_sqs_conn, the_queue_name ) :
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

    return a_data_name, a_next_queue_suffix


#--------------------------------------------------------------------------------------
an_usage = \
"""
%prog \\
      --task-def-dir=~/rackspace \\
      --rackspace-user=${RACKSPACE_USER} \\
      --rackspace-key=${RACKSPACE_KEY} \\
      --aws-access-key-id=${AWS_ACCESS_KEY_ID} \\
      --aws-secret-access-key=${AWS_SECRET_ACCESS_KEY}
"""

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--container-name",
                            metavar = "< name of task container >",
                            action = "store",
                            dest = "container_name" )

a_option_parser.add_option( "--output-dir",
                            metavar = "< location of the task defintion >",
                            action = "store",
                            dest = "output_dir",
                            help = "(\"%default\", by default)",
                            default = "." )

a_option_parser.add_option( "--rackspace-user",
                            metavar = "< Rackspace user >",
                            action = "store",
                            dest = "rackspace_user",
                            help = "(${RACKSPACE_USER}, by default)",
                            default = os.getenv( "RACKSPACE_USER" ) )
    
a_option_parser.add_option( "--rackspace-key",
                            metavar = "< Rackspace key >",
                            action = "store",
                            dest = "rackspace_key",
                            help = "(${RACKSPACE_KEY}, by default)",
                            default = os.getenv( "RACKSPACE_KEY" ) )
    
a_option_parser.add_option( "--aws-access-key-id",
                            metavar = "< Amazon key id >",
                            action = "store",
                            dest = "aws_access_key_id",
                            help = "(${AWS_ACCESS_KEY_ID}, by default)",
                            default = os.getenv( "AWS_ACCESS_KEY_ID" ) )
    
a_option_parser.add_option( "--aws-secret-access-key",
                            metavar = "< Amazon secret key >",
                            action = "store",
                            dest = "aws_secret_access_key",
                            help = "(${AWS_SECRET_ACCESS_KEY}, by default)",
                            default = os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    

#--------------------------------------------------------------------------------------
if __name__ == '__main__' :
    an_options, an_args = a_option_parser.parse_args()

    # Check command line arguments first
    a_container_name = an_options.container_name
    if an_options.container_name == None :
        print "Please, use '--task-container-name' to define corresponding value"
        os._exit( os.EX_USAGE )
        pass

    import os.path, shutil
    an_options.output_dir = os.path.abspath( an_options.output_dir )
    an_output_dir = os.path.join( an_options.output_dir, a_container_name )
    shutil.rmtree( an_output_dir, True )
    os.makedirs( an_output_dir )
    if not os.path.isdir( an_output_dir ) :
        print "Couild not create output directory"
        os._exit( os.EX_USAGE )
        pass

    RACKSPACE_USER = an_options.rackspace_user
    if RACKSPACE_USER == None :
        print "Define RACKSPACE_USER parameter through '--rackspace-user' option"
        os._exit( os.EX_USAGE )
        pass

    RACKSPACE_KEY = an_options.rackspace_key
    if RACKSPACE_KEY == None :
        print "Define RACKSPACE_KEY parameter through '--rackspace-key' option"
        os._exit( os.EX_USAGE )
        pass

    AWS_ACCESS_KEY_ID = an_options.aws_access_key_id
    if AWS_ACCESS_KEY_ID == None :
        print "Define AWS_ACCESS_KEY_ID parameter through '--aws-access-key-id' option"
        os._exit( os.EX_USAGE )
        pass

    AWS_SECRET_ACCESS_KEY = an_options.aws_secret_access_key
    if AWS_SECRET_ACCESS_KEY == None :
        print "Define AWS_SECRET_ACCESS_KEY parameter through '--aws-secret-access-key' option"
        os._exit( os.EX_USAGE )
        pass


    #---------------------------------------------------------------------------
    import cloudfiles
    a_cloudfiles_conn = cloudfiles.get_connection( RACKSPACE_USER, RACKSPACE_KEY, timeout = 500 )
    a_cloudfiles_container = a_cloudfiles_conn[ a_container_name ]

    import boto
    a_queue_name = an_options.container_name
    a_sqs_conn = boto.connect_sqs( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    a_queue_suffix = ''
    while True :
        a_queue_name = '%s___%s' % ( a_container_name, a_queue_suffix )
        print a_queue_name, 
        a_data_name, a_queue_suffix = get_message( a_sqs_conn, a_queue_name )
        print a_data_name, a_queue_suffix

        if a_data_name == '*' and a_queue_suffix == '*':
            break

        # To secure the following 'save' operation
        a_file_path = os.path.join( an_output_dir, a_data_name )
        shutil.rmtree( a_file_path, True ) 
        print not os.path.isfile( a_file_path ),

        a_file_object = a_cloudfiles_container.get_object( a_data_name )
        a_file_object.save_to_filename( a_file_path )
        print a_file_path, os.path.isfile( a_file_path )

        pass
 
    
    #---------------------------------------------------------------------------
    import os
    os._exit( os.EX_OK )

    pass


#--------------------------------------------------------------------------------------
