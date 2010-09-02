

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

import os, os.path, hashlib


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
                                  default = None )
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


#--------------------------------------------------------------------------------------
def get_root_object( the_s3_conn ) :
    "Looking for study root"
    a_backet_id = the_s3_conn.get_canonical_user_id()
    a_bucket_name = hashlib.md5( a_backet_id ).hexdigest()

    a_bucket = None
    try :
        a_bucket = the_s3_conn.get_bucket( a_bucket_name )
    except :
        a_bucket = the_s3_conn.create_bucket( a_bucket_name )
        pass

    return a_bucket, a_backet_id


#--------------------------------------------------------------------------------------
class TRootObject :
    "Represents S3 dedicated implementation of study root"

    def __init__( self, the_s3_conn, the_bucket, the_id ) :
        "Use static corresponding functions to an instance of this class"
        self.connection = the_s3_conn
        self.bucket = the_bucket
        self.id = the_id

        pass
    
    @staticmethod
    def get( the_s3_conn ) :
        a_bucket, an_id = get_root_object( the_s3_conn )

        return TRootObject( the_s3_conn, a_bucket, an_id )
    
    pass


#--------------------------------------------------------------------------------------
def api_version() :

    return '0.1'


#--------------------------------------------------------------------------------------
def _id_separator( the_api_version ) :
    if the_api_version == 'dummy' :
        return '|'

    return ' | '


#--------------------------------------------------------------------------------------
def generate_id( the_parent_id, the_child_name, the_api_version ) :
    a_separator = _id_separator( the_api_version )
    a_child_id = '%s%s%s' % ( the_parent_id, a_separator, the_child_name )

    a_bucket_name = hashlib.md5( a_child_id ).hexdigest()

    return a_child_id, a_bucket_name


#--------------------------------------------------------------------------------------
def _decorate_key_name( the_name ) :
    # This workaround make possible to use '/' symbol at the beginning of the key name

    return '!%s' % the_name


#--------------------------------------------------------------------------------------
def get_name( the_key ) :

    return the_key.name[ 1 : ]


#--------------------------------------------------------------------------------------
def get_key( the_parent_bucket, the_name ) :
    a_decorated_name = _decorate_key_name( the_name )

    return Key( the_parent_bucket, a_decorated_name )


#--------------------------------------------------------------------------------------
def create_object( the_s3_conn, the_parent_bucket, the_parent_id, the_name, the_attr ) :
    a_study_key = get_key( the_parent_bucket, the_name )

    a_study_key.set_contents_from_string( the_attr )

    a_backet_id, a_bucket_name = generate_id( the_parent_id, the_name, api_version() )
    
    a_bucket = the_s3_conn.create_bucket( a_bucket_name )

    return a_bucket, a_backet_id


#--------------------------------------------------------------------------------------
def get_object( the_s3_conn, the_parent_id, the_name, the_api_version ) :
    a_backet_id, a_bucket_name = generate_id( the_parent_id, the_name, the_api_version )
    
    a_bucket = the_s3_conn.get_bucket( a_bucket_name )

    return a_bucket, a_backet_id


#--------------------------------------------------------------------------------------
def create_study_object( the_s3_conn, the_root_bucket, the_root_id, the_study_name ) :
    "Registering the new study"

    return create_object( the_s3_conn, the_root_bucket, the_root_id, the_study_name, api_version() )


#--------------------------------------------------------------------------------------
def get_study_object( the_s3_conn, the_root_id, the_study_name, the_api_version ) :
    "Registering the new study"

    return get_object( the_s3_conn, the_root_id, the_study_name, the_api_version )


#--------------------------------------------------------------------------------------
def get_study_key( the_root_bucket, the_study_name ) :

    return get_key( the_root_bucket, the_study_name )


#--------------------------------------------------------------------------------------
def extract_study_props( the_root_bucket, the_study_name ) :
    a_study_key = get_key( the_root_bucket, the_study_name )

    an_api_version = a_study_key.get_contents_as_string()

    return an_api_version


#--------------------------------------------------------------------------------------
def create_file_object( the_s3_conn, the_study_bucket, the_study_id, the_file_path, the_hex_md5 ) :
    
    return create_object( the_s3_conn, the_study_bucket, the_study_id, the_file_path, the_hex_md5 )


#--------------------------------------------------------------------------------------
def get_file_key( the_root_bucket, the_file_path ) :

    return get_key( the_root_bucket, the_file_path )


#--------------------------------------------------------------------------------------
def extract_file_props( the_file_key, the_api_version ) :
    a_hex_md5 = the_file_key_name.get_contents_as_string()

    a_file_path = get_name( the_file_key, the_api_version )

    return a_hex_md5, a_file_path


#--------------------------------------------------------------------------------------
def _item_key_separator( the_api_version ) :
    if the_api_version == 'dummy' :
        return ':'

    return ' % '


#--------------------------------------------------------------------------------------
def generate_item_key( the_hex_md5, the_file_item, the_api_version ) :
    a_separator = _item_key_separator( the_api_version )

    if the_api_version == 'dummy' :
        return '%s%s%s' % ( the_file_item, a_separator, the_hex_md5 )

    return '%s%s%s' % ( the_hex_md5, a_separator, the_file_item )


#--------------------------------------------------------------------------------------
def extract_item_props( the_file_item_key_name, the_api_version ) :
    a_separator = _item_key_separator( the_api_version )

    a_file_name, a_hex_md5 = None, None

    if the_api_version == 'dummy' :
        a_file_name, a_hex_md5 = the_file_item_key_name.split( a_separator )
    else:
        a_hex_md5, a_file_name = the_file_item_key_name.split( a_separator )
        pass

    return a_hex_md5, a_file_name


#--------------------------------------------------------------------------------------
def generate_uploading_dir( the_file_path ) :
    a_file_dirname = os.path.dirname( the_file_path )
    a_file_basename = os.path.basename( the_file_path )

    a_sub_folder = hashlib.md5( a_file_basename ).hexdigest()
    a_working_dir = os.path.join( a_file_dirname, a_sub_folder )
    
    return a_working_dir


#--------------------------------------------------------------------------------------
