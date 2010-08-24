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
from balloon.common import print_d, print_i, print_e, sh_command, ssh_command, Timer, Worker

import balloon.amazon as amazon

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
def upload_file( the_s3_conn, the_worker, the_study_file_key, the_study_id, the_printing_depth ) :
    a_file_dirname = os.path.dirname( the_study_file_key.key )
    a_file_basename = os.path.basename( the_study_file_key.key )

    print_d( "the_study_file_key = %s\n" % the_study_file_key, the_printing_depth )

    a_working_dir = the_study_file_key.key.split( ':' )[ -1 ]
    print_d( "a_working_dir = '%s'\n" % a_working_dir, the_printing_depth )

    a_file_id = '%s/%s' % ( the_study_id, the_study_file_key.key )
    print_d( "a_file_id = '%s'\n" % a_file_id, the_printing_depth )

    a_file_bucket_name = hashlib.md5( a_file_id ).hexdigest()

    a_file_bucket = the_s3_conn.get_bucket( a_file_bucket_name )
    print_d( "a_file_bucket = %s\n" % a_file_bucket, the_printing_depth )

    amazon.upload_items( the_worker, a_file_bucket, a_working_dir, the_printing_depth + 1 )

    pass


#------------------------------------------------------------------------------------------
class UploadFile :
    def __init__( self, the_s3_conn, the_worker, the_study_file_key, the_study_id, the_printing_depth ) :
        self.worker = the_worker
        self.s3_conn = the_s3_conn
        self.study_file_key = the_study_file_key
        self.study_id = the_study_id
        self.printing_depth = the_printing_depth
        pass
    
    def run( self ) :
        upload_file( self.s3_conn, self.worker, self.study_file_key, self.study_id, self.printing_depth )

        return self

    pass


#------------------------------------------------------------------------------------------
def upload_files( the_s3_conn, the_number_threads, the_study_bucket, the_study_id, the_printing_depth ) :
    a_study_file_keys = the_study_bucket.get_all_keys()
    a_worker = Worker( the_number_threads + len( a_study_file_keys ) )

    for a_study_file_key in a_study_file_keys :
        a_task = UploadFile( the_s3_conn, a_worker, a_study_file_key, the_study_id, the_printing_depth )

        a_worker.put( a_task )
        
        pass

    a_worker.join()

    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --study-name='my interrupted study' --number-threads=7"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--study-name",
                            metavar = "< an unique name of the user study >",
                            action = "store",
                            dest = "study_name" )
a_option_parser.add_option( "--number-threads",
                            metavar = "< number of threads to use >",
                            type = "int",
                            action = "store",
                            dest = "number_threads",
                            help = "(\"%default\", by default)",
                            default = 8 )
a_option_parser.add_option( "--socket-timeout",
                            metavar = "< socket timeout time >",
                            type = "int",
                            action = "store",
                            dest = "socket_timeout",
                            help = "(\"%default\", by default)",
                            default = 0 )
common.add_parser_options( a_option_parser )
amazon.add_parser_options( a_option_parser )
    
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

a_study_name = an_options.study_name
    
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

if an_options.number_threads < 1 :
    a_option_parser.error( "'--number-threads' must be at least 1" )
    pass

try:
    import socket
    # socket.setdefaulttimeout( an_options.socket_timeout )
except TypeError, exc :
    print_e( "'--socket-timeout' error: %s" % exc.message )
    pass


print_i( "--------------------------- Connecting to Amazon S3 -----------------------------\n" )
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )


print_i( "----------------------- Looking for the appoined study --------------------------\n" )
a_canonical_user_id = a_s3_conn.get_canonical_user_id()
a_study_id = '%s/%s' % ( a_canonical_user_id, a_study_name )
a_study_bucket_name = hashlib.md5( a_study_id ).hexdigest()
print_d( "a_study_id = '%s'\n" % a_study_id )

a_study_bucket = a_s3_conn.get_bucket( a_study_bucket_name )
print_d( "a_study_bucket = '%s'\n" % a_study_bucket )


print_i( "---------------------------- Uploading study files ------------------------------\n" )
a_data_loading_time = Timer()

upload_files( a_s3_conn, an_options.number_threads, a_study_bucket, a_study_id, 1 )

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_i( "-------------------------------------- OK ---------------------------------------\n" )
print a_study_name


#------------------------------------------------------------------------------------------
