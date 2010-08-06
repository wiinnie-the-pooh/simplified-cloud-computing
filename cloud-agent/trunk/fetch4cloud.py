#!/usr/bin/env python


#--------------------------------------------------------------------------------------
"""
This script is responsible for fetching of the task resulting data from the cloud
"""


#--------------------------------------------------------------------------------------
import os


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
                            help = "(\"%default\", by default)",
                            default = os.getenv( "RACKSPACE_USER" ) )
    
a_option_parser.add_option( "--rackspace-key",
                            metavar = "< Rackspace key >",
                            action = "store",
                            dest = "rackspace_key",
                            help = "(\"%default\", by default)",
                            default = os.getenv( "RACKSPACE_KEY" ) )
    
a_option_parser.add_option( "--aws-access-key-id",
                            metavar = "< Amazon key id >",
                            action = "store",
                            dest = "aws_access_key_id",
                            help = "(\"%default\", by default)",
                            default = os.getenv( "AWS_ACCESS_KEY_ID" ) )
    
a_option_parser.add_option( "--aws-secret-access-key",
                            metavar = "< Amazon secret key >",
                            action = "store",
                            dest = "aws_secret_access_key",
                            help = "(\"%default\", by default)",
                            default = os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    

#--------------------------------------------------------------------------------------
if __name__ == '__main__' :
    an_options, an_args = a_option_parser.parse_args()

    # Check command line arguments first
    if an_options.container_name == None :
        print "Please, use '--task-container-name' to define corresponding value"
        os._exit( os.EX_USAGE )
        pass

    import os.path, shutil
    an_options.output_dir = os.path.abspath( an_options.output_dir )
    an_output_dir = os.path.join( an_options.output_dir, "output" )
    shutil.rmtree( an_output_dir, True )
    os.makedirs( an_output_dir )
    if not os.path.isdir( an_output_dir ) :
        print "Couild not create output directory"
        os._exit( os.EX_USAGE )
        pass

    RACKSPACE_USER = an_options.rackspace_user
    RACKSPACE_KEY = an_options.rackspace_key

    AWS_ACCESS_KEY_ID = an_options.aws_access_key_id
    AWS_SECRET_ACCESS_KEY = an_options.aws_secret_access_key


    #---------------------------------------------------------------------------
    import boto
    a_container_name = an_options.container_name
    a_sqs_conn = boto.connect_sqs( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    a_sqs_queue = a_sqs_conn.create_queue( a_container_name )
    while True :
        a_message = a_sqs_queue.read()
        if a_message == None :
            continue

        a_message_body = a_message.get_body()
        a_sqs_queue.delete_message( a_message )
        print a_message_body
        if a_message_body == 'finish' :
            break;
        pass

    a_sqs_queue.delete()
    
    
    #---------------------------------------------------------------------------
    import os
    os._exit( os.EX_OK )

    pass


#--------------------------------------------------------------------------------------
