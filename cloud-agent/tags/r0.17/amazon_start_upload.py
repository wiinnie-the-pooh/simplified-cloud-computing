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


#------------------------------------------------------------------------------------------
"""
This script is responsible for efficient uploading of multi file data
"""


#------------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command, ssh_command
from balloon.common import generate_id, generate_file_key, generate_item_key
from balloon.common import extract_file_props, extract_item_props
from balloon.common import study_api_version, file_api_version
from balloon.common import generate_uploading_dir
from balloon.common import Timer, WorkerPool, compute_md5

import balloon.amazon as amazon
from balloon.amazon import mark_api_version, extract_api_version

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
def upload_file( the_worker_pool, the_file_path, the_study_bucket, the_study_id, the_upload_item_size, the_printing_depth ) :
    a_working_dir = generate_uploading_dir( the_file_path )

    import shutil
    shutil.rmtree( a_working_dir, True )
    os.makedirs( a_working_dir )
    print_d( "a_working_dir = '%s'\n" % a_working_dir, the_printing_depth )

    a_file_dirname = os.path.dirname( the_file_path )
    a_file_basename = os.path.basename( the_file_path )

    import tempfile
    a_tmp_file = tempfile.mkstemp( dir = a_working_dir )[ 1 ]
    # a_tmp_file = tempfile.mkstemp()[ 1 ] # use this work arround for FAT file systems
    sh_command( "cd '%s' &&  tar -czf %s '%s'" % 
                ( a_file_dirname, a_tmp_file, a_file_basename ), the_printing_depth )

    a_statinfo = os.stat( a_tmp_file )
    print_d( "a_statinfo.st_size = %d, bytes\n" % a_statinfo.st_size, the_printing_depth )

    import math
    a_suffix_length = math.log10( float( a_statinfo.st_size ) / the_upload_item_size )
    if a_suffix_length > 0 :
        a_suffix_length = int( a_suffix_length + 1.0 )
    else:
        a_suffix_length = 0
        pass
    print_d( "a_suffix_length = %d, digits\n" % a_suffix_length, the_printing_depth )

    a_file_item_target = os.path.join( a_working_dir, a_file_basename )
    sh_command( "cat '%s' | split --bytes=%d --numeric-suffixes --suffix-length=%d - %s.tgz-" % 
                ( a_tmp_file, the_upload_item_size, a_suffix_length, a_file_item_target ), the_printing_depth )

    a_file_pointer = open( a_tmp_file, 'rb' )
    a_md5 = compute_md5( a_file_pointer )
    a_hex_md5, a_base64md5 = a_md5

    a_file_pointer.close()
    os.remove( a_tmp_file )

    a_file_api_version = file_api_version()
    print_d( "a_file_api_version = '%s'\n" % a_file_api_version, the_printing_depth )

    a_study_file_key = Key( the_study_bucket )
    a_study_file_key.key = generate_file_key( a_hex_md5, the_file_path, a_file_api_version )
    mark_api_version( a_study_file_key, a_file_api_version )
    print_d( "a_study_file_key = %s\n" % a_study_file_key, the_printing_depth )

    a_file_id, a_file_bucket_name = generate_id( the_study_id, a_study_file_key.name, a_file_api_version )
    print_d( "a_file_id = '%s'\n" % a_file_id, the_printing_depth )
    
    a_file_bucket = a_s3_conn.create_bucket( a_file_bucket_name )
    print_d( "a_file_bucket = %s\n" % a_file_bucket, the_printing_depth )

    pass


#------------------------------------------------------------------------------------------
def upload_files( the_files, the_study_bucket, the_study_id, the_upload_item_size, the_printing_depth ) :
    a_worker_pool = WorkerPool( len( the_files ) )

    for a_file_path in the_files :
        a_worker_pool.charge( upload_file, ( a_worker_pool, a_file_path, the_study_bucket, the_study_id, the_upload_item_size, the_printing_depth ) )

        pass

    a_worker_pool.shutdown()
    a_worker_pool.join()
    
    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --study-name='my favorite study' --upload-item-size=5160 --socket-timeout=3"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += " <file 1> <file 2> ..."

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--study-name",
                            metavar = "< an unique name of the user study >",
                            action = "store",
                            dest = "study_name",
                            help = "(UUID generated, by default)",
                            default = str( uuid.uuid4() ) )
a_option_parser.add_option( "--upload-item-size",
                            metavar = "< size of file pieces to be uploaded, in bytes >",
                            type = "int",
                            action = "store",
                            dest = "upload_item_size",
                            help = "(\"%default\", by default)",
                            default = 10240 )
a_option_parser.add_option( "--socket-timeout",
                            metavar = "< socket timeout time >",
                            type = "int",
                            action = "store",
                            dest = "socket_timeout",
                            help = "(\"%default\", by default)",
                            default = 1 )
common.add_parser_options( a_option_parser )
amazon.add_parser_options( a_option_parser )
    
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

a_files = list()
for an_arg in an_args :
    if not os.path.exists( an_arg ) :
        a_option_parser.error( "The given file should exists\n" )
        pass
    a_files.append( os.path.abspath( an_arg ) )
    pass

if len( a_files ) == 0 :
    a_option_parser.error( "You should define one valid 'file' at least\n" )
    pass

print_d( "a_files = %r\n" % a_files )

a_study_name = an_options.study_name
print_d( "a_study_name = '%s'\n" % a_study_name )
    
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

import socket
socket.setdefaulttimeout( an_options.socket_timeout )


print_i( "--------------------------- Connecting to Amazon S3 -----------------------------\n" )
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )


print_i( "--------------------------- Looking for study root ------------------------------\n" )
a_canonical_user_id = a_s3_conn.get_canonical_user_id()
print_d( "a_canonical_user_id = '%s'\n" % a_canonical_user_id )

a_root_bucket_name = hashlib.md5( a_canonical_user_id ).hexdigest()
a_root_bucket = None
try :
    a_root_bucket = a_s3_conn.get_bucket( a_root_bucket_name )
except :
    print_d( "Not root was found, creating a new one - " )
    a_root_bucket = a_s3_conn.create_bucket( a_root_bucket_name )
    pass

print_d( "a_root_bucket = %s\n" % a_root_bucket )


print_i( "------------------------- Registering the new study -----------------------------\n" )
a_study_api_version = study_api_version()
print_d( "a_study_api_version = '%s'\n" % a_study_api_version )

a_study_key = Key( a_root_bucket )
a_study_key.key = '%s' % ( a_study_name )
mark_api_version( a_study_key, study_api_version() )
print_d( "a_study_key = %s\n" % a_study_key )

a_study_id, a_study_bucket_name = generate_id( a_canonical_user_id, a_study_name, a_study_api_version )
print_d( "a_study_id = '%s'\n" % a_study_id )

a_study_bucket = a_s3_conn.create_bucket( a_study_bucket_name )
print_d( "a_study_bucket = '%s'\n" % a_study_bucket )


print_i( "---------------------------- Uploading study files ------------------------------\n" )
a_data_loading_time = Timer()

upload_files( a_files, a_study_bucket, a_study_id, an_options.upload_item_size, 0 )

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_i( "-------------------------------------- OK ---------------------------------------\n" )
print a_study_name


#------------------------------------------------------------------------------------------
