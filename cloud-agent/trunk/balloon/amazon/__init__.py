

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
class TRootObject :
    "Represents S3 dedicated implementation of study root"

    def __init__( self, the_s3_conn, the_bucket, the_id ) :
        "Use static corresponding functions to an instance of this class"
        self._connection = the_s3_conn

        self._bucket = the_bucket
        self._id = the_id

        pass
    
    def __str__( self ) :

        return "'%s'- %s" % ( self._id, self._bucket )

    @staticmethod
    def get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY ) :
        "Looking for study root"
        import boto
        a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
        an_id = a_s3_conn.get_canonical_user_id()

        import hashlib
        a_bucket_name = hashlib.md5( an_id ).hexdigest()

        a_bucket = None
        try :
            a_bucket = a_s3_conn.get_bucket( a_bucket_name )
        except :
            a_bucket = a_s3_conn.create_bucket( a_bucket_name )
            pass
        
        return TRootObject( a_s3_conn, a_bucket, an_id )
    
    def _next( self ) :
        for a_study_key in self._bucket.list() :
            yield TStudyObject.get( self, get_key_name( a_study_key ) )
            
            pass
        
        pass

    def __iter__( self ) :
        "Iterates through study files"
        
        return self._next()

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

    return '# %s' % the_name


#--------------------------------------------------------------------------------------
def get_key_name( the_key ) :

    return the_key.name[ 2 : ]


#--------------------------------------------------------------------------------------
def get_key( the_parent_bucket, the_name ) :
    a_decorated_name = _decorate_key_name( the_name )

    return Key( the_parent_bucket, a_decorated_name )


#--------------------------------------------------------------------------------------
class TStudyObject :
    "Represents S3 dedicated implementation of study object"

    def __init__( self, the_root_object, the_key, the_bucket, the_id, the_api_version ) :
        "Use static corresponding functions to an instance of this class"
        self._root_object = the_root_object

        self._key = the_key
        self._bucket = the_bucket
        self._id = the_id

        self._api_version = the_api_version

        pass
    
    def connection( self ) :

        return self._root_object._connection

    def __str__( self ) :

        return "'%s' - %s - %s" % ( self._id, self._api_version, self._bucket )

    @staticmethod
    def create( the_root_object, the_study_name ) :
        a_key = get_key( the_root_object._bucket, the_study_name )

        an_api_version = api_version()

        a_key.set_contents_from_string( an_api_version )

        an_id, a_bucket_name = generate_id( the_root_object._id, the_study_name, an_api_version )
    
        a_bucket = the_root_object._connection.create_bucket( a_bucket_name )

        return TStudyObject( the_root_object, a_key, a_bucket, an_id, an_api_version )

    @staticmethod
    def get( the_root_object, the_study_name ) :
        a_key = get_key( the_root_object._bucket, the_study_name )

        an_api_version = a_key.get_contents_as_string()

        an_id, a_bucket_name = generate_id( the_root_object._id, the_study_name, an_api_version )
    
        a_bucket = the_root_object._connection.get_bucket( a_bucket_name )
    
        return TStudyObject( the_root_object, a_key, a_bucket, an_id, an_api_version )

    def _next( self ) :
        for a_file_key in self._bucket.list() :
            yield TFileObject.get( self, get_key_name( a_file_key ) )
            
            pass
        
        pass

    def __iter__( self ) :
        "Iterates through study files"
        
        return self._next()

    pass


#--------------------------------------------------------------------------------------
def generate_uploading_dir( the_file_path ) :
    a_file_dirname = os.path.dirname( the_file_path )
    a_file_basename = os.path.basename( the_file_path )

    a_sub_folder = hashlib.md5( a_file_basename ).hexdigest()
    a_working_dir = os.path.join( a_file_dirname, a_sub_folder )
    
    return a_working_dir


#--------------------------------------------------------------------------------------
class TFileObject :
    "Represents S3 dedicated implementation of file object"

    def __init__( self, the_study_object, the_key, the_bucket, the_id, the_hex_md5 ) :
        "Use static corresponding functions to an instance of this class"
        self._study_object = the_study_object

        self._key = the_key
        self._bucket = the_bucket
        self._id = the_id

        self._hex_md5 = the_hex_md5

        pass
    
    def file_path( self ) :

        return get_key_name( self._key )

    def hex_md5( self ) :

        return self._hex_md5

    def connection( self ) :

        return self._study_object._connection

    def api_version( self ) :

        return self._study_object._api_version

    def __str__( self ) :

        return "'%s' - %s" % ( self._id, self._bucket )

    @staticmethod
    def create( the_study_object, the_file_path, the_hex_md5 ) :
        a_key = get_key( the_study_object._bucket, the_file_path )

        a_key.set_contents_from_string( the_hex_md5 )

        an_api_version = the_study_object._api_version

        an_id, a_bucket_name = generate_id( the_study_object._id, the_file_path, an_api_version )
    
        a_bucket = the_study_object.connection().create_bucket( a_bucket_name )

        return TFileObject( the_study_object, a_key, a_bucket, an_id, the_hex_md5 )

    @staticmethod
    def get( the_study_object, the_file_path ) :
        a_key = get_key( the_study_object._bucket, the_file_path )

        a_hex_md5 = a_key.get_contents_as_string()

        an_api_version = the_study_object._api_version

        an_id, a_bucket_name = generate_id( the_study_object._id, the_file_path, an_api_version )

        a_bucket = the_study_object.connection().get_bucket( a_bucket_name )

        return TFileObject( the_study_object, a_key, a_bucket, an_id, a_hex_md5 )

    def _next( self ) :
        for an_item_key in self._bucket.list() :
            yield TItemObject.get( self, an_item_key )
            
            pass
        
        pass

    def __iter__( self ) :
        "Iterates through file items"
        
        return self._next()

    def seal_name( self ) :

        return self._bucket.name

    def seal( self, the_working_dir ) :
        "To mark the everything was sucessfuly uploaded"
        os.rmdir( the_working_dir )

        # To mark that final file item have been sucessfully uploaded
        an_item_key = get_key( self._bucket, self.seal_name() )
        an_item_key.set_contents_from_string( 'dummy' )

        pass

    pass


#--------------------------------------------------------------------------------------
def _item_key_separator( the_api_version ) :
    if the_api_version == 'dummy' :
        return ':'

    return ' % '


#--------------------------------------------------------------------------------------
def generate_item_name( the_hex_md5, the_file_item, the_api_version ) :
    a_separator = _item_key_separator( the_api_version )

    if the_api_version == 'dummy' :
        return '%s%s%s' % ( the_file_item, a_separator, the_hex_md5 )

    return '%s%s%s' % ( the_hex_md5, a_separator, the_file_item )


#--------------------------------------------------------------------------------------
def extract_item_props( the_item_key_name, the_api_version ) :
    a_separator = _item_key_separator( the_api_version )

    an_item_name, a_hex_md5 = None, None
    try :
        if the_api_version == 'dummy' :
            an_item_name, a_hex_md5 = the_item_key_name.split( a_separator )
        else:
            a_hex_md5, an_item_name = the_item_key_name.split( a_separator )
            pass
    except :
        pass

    return a_hex_md5, an_item_name


#--------------------------------------------------------------------------------------
class TItemObject :
    "Represents S3 dedicated implementation of item object"

    def __init__( self, the_file_object, the_key, the_name, the_hex_md5 ) :
        "Use static corresponding functions to an instance of this class"
        self._file_object = the_file_object

        self._key = the_key
        self._name = the_name
        self._hex_md5 = the_hex_md5

        pass
    
    def name( self ) :

        return self._name

    def hex_md5( self ) :

        return self._hex_md5

    def is_seal( self ) :
        
        return self._name == None

    def download( self, the_file_path ) :
        self._key.get_contents_to_filename( the_file_path )

        pass

    def __str__( self ) :

        return "%s" % ( self._key )

    @staticmethod
    def create( the_file_object, the_item_name, the_item_path ) :
        a_file_pointer = open( the_item_path, 'rb' )

        from balloon.common import compute_md5
        a_md5 = compute_md5( a_file_pointer )
        a_hex_md5, a_base64md5 = a_md5

        an_api_version = the_file_object.api_version()
        an_item_name = generate_item_name( a_hex_md5, the_item_name, an_api_version )

        an_item_key = get_key( the_file_object._bucket, an_item_name )
        # a_part_key.set_contents_from_file( a_file_pointer, md5 = a_md5 ) # this method is not thread safe
        an_item_key.set_contents_from_file( a_file_pointer)
        
        os.remove( the_item_path )

        return TItemObject( the_file_object, an_item_key, the_item_name, a_hex_md5 )

    @staticmethod
    def get( the_file_object, the_item_key ) :
        an_api_version = the_file_object.api_version()

        a_hex_md5, a_item_name = extract_item_props( get_key_name( the_item_key ), an_api_version )

        return TItemObject( the_file_object, the_item_key, a_item_name, a_hex_md5 )

    pass


#--------------------------------------------------------------------------------------
