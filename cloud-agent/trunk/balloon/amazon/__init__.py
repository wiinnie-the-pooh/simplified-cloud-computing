

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
from balloon.common import print_e, print_d, ssh_command

import boto
from boto.s3.key import Key

import os, os.path


#--------------------------------------------------------------------------------------
def add_usage_description() :
    return " --aws-access-key-id=${AWS_ACCESS_KEY_ID} --aws-secret-access-key=${AWS_SECRET_ACCESS_KEY}"


#--------------------------------------------------------------------------------------
def add_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--aws-access-key-id",
                                  metavar = "< Amazon key id >",
                                  action = "store",
                                  dest = "aws_access_key_id",
                                  help = "(${AWS_ACCESS_KEY_ID}, by default)",
                                  default = os.getenv( "AWS_ACCESS_KEY_ID" ) )
    
    the_option_parser.add_option( "--aws-secret-access-key",
                                  metavar = "< Amazon secret key >",
                                  action = "store",
                                  dest = "aws_secret_access_key",
                                  help = "(${AWS_SECRET_ACCESS_KEY}, by default)",
                                  default = os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    pass


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    AWS_ACCESS_KEY_ID = the_options.aws_access_key_id
    if AWS_ACCESS_KEY_ID == None :
        print_e( "Define AWS_ACCESS_KEY_ID parameter through '--aws-access-key-id' option\n" )
        pass

    AWS_SECRET_ACCESS_KEY = the_options.aws_secret_access_key
    if AWS_SECRET_ACCESS_KEY == None :
        print_e( "Define AWS_SECRET_ACCESS_KEY parameter through '--aws-secret-access-key' option\n" )
        pass

    return AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


#--------------------------------------------------------------------------------------
def add_threading_usage_description() :
    return " --number-threads=7"


#--------------------------------------------------------------------------------------
def add_threading_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--number-threads",
                                  metavar = "< number of threads to use >",
                                  type = "int",
                                  action = "store",
                                  dest = "number_threads",
                                  help = "(\"%default\", by default)",
                                  default = 2 )
    pass


#--------------------------------------------------------------------------------------
def extract_threading_options( the_options, the_option_parser ) :
    if the_options.number_threads < 1 :
        the_option_parser.error( "'--number-threads' must be at least 1" )
        pass

    return the_options.number_threads


#--------------------------------------------------------------------------------------
def add_timeout_usage_description() :
    return " --socket-timeout=3"


#--------------------------------------------------------------------------------------
def add_timeout_options( the_option_parser ) :
    the_option_parser.add_option( "--socket-timeout",
                                  metavar = "< socket timeout time >",
                                  type = "int",
                                  action = "store",
                                  dest = "socket_timeout",
                                  help = "(\"%default\", by default)",
                                  default = 1 )
    pass


#--------------------------------------------------------------------------------------
def extract_timeout_options( the_options, the_option_parser ) :
    import socket
    socket.setdefaulttimeout( the_options.socket_timeout )

    return the_options.socket_timeout


#--------------------------------------------------------------------------------------
def wait_activation( the_instance, the_ssh_connect, the_ssh_client ) :
    while True :
        try :
            print_d( '%s ' % the_instance.update() )
            break
        except :
            continue
        pass
    
    # Making sure that corresponding instances are ready to use
    while True :
        try :
            if the_instance.update() == 'running' :
                break
            print_d( '.' )
        except :
            continue
        pass
    
    print_d( ' %s\n' % the_instance.update() )

    while True :
        try :
            the_ssh_connect()
            ssh_command( the_ssh_client, 'echo  > /dev/null' )
            break
        except :
            continue
        pass

    pass


#------------------------------------------------------------------------------------------
def mark_if_finished( the_working_dir, the_file_bucket, the_printing_depth ) :
    try :
        os.rmdir( the_working_dir )

        # To mark that final file item have been sucessfully uploaded
        a_part_key = Key( the_file_bucket )
        a_part_key.key = the_file_bucket.name
        a_part_key.set_contents_from_string( 'dummy' )

        print_d( "%s\n" % a_part_key, the_printing_depth )

        return True
    except :
        pass

    return False


#------------------------------------------------------------------------------------------
def upload_item( the_file_item, the_working_dir, the_file_bucket, the_printing_depth ) :
    "Uploading file item"
    try :
        a_file_path = os.path.join( the_working_dir, the_file_item )
        print_d( "'%s'\n" % a_file_path, the_printing_depth )
        
        a_part_key = Key( the_file_bucket )
        a_part_key.key = the_file_item
        a_part_key.set_contents_from_filename( a_file_path )
        print_d( "%s\n" % a_part_key, the_printing_depth + 1 )
        
        os.remove( a_file_path )
        
    except :
        pass

    mark_if_finished( the_working_dir, the_file_bucket, the_printing_depth )

    return True


#------------------------------------------------------------------------------------------
def upload_items( the_worker_pool, the_file_bucket, the_working_dir, the_printing_depth ) :
    "Uploading file items"

    a_file_bucket_names = [ an_item_key.name for an_item_key in the_file_bucket.get_all_keys() ]

    a_dir_contents = os.listdir( the_working_dir )

    a_dir_contents.sort()
    a_dir_contents.reverse()

    for a_file_item in a_dir_contents :
        if a_file_item in a_file_bucket_names :
            a_file_path = os.path.join( the_working_dir, a_file_item )
            os.remove( a_file_path )

            continue

        the_worker_pool.charge( upload_item, [ a_file_item, the_working_dir, the_file_bucket, the_printing_depth + 1 ] )

        pass

    return True


#--------------------------------------------------------------------------------------
