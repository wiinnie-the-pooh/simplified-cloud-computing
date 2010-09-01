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
def mark_finished( the_working_dir, the_file_bucket, the_printing_depth ) :
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
def upload_item( the_file_item, the_file_path, the_file_bucket, the_file_api_version, the_printing_depth ) :
    "Uploading file item"
    try :
        a_part_key = Key( the_file_bucket )

        a_file_pointer = open( the_file_path, 'rb' )
        a_md5 = compute_md5( a_file_pointer )
        a_hex_md5, a_base64md5 = a_md5

        a_part_key.key = generate_item_key( a_hex_md5, the_file_item, the_file_api_version )

        # a_part_key.set_contents_from_file( a_file_pointer, md5 = a_md5 ) # this method is not thread safe
        a_part_key.set_contents_from_file( a_file_pointer)
        print_d( "%s\n" % a_part_key, the_printing_depth + 1 )
        
        os.remove( the_file_path )
        
        return True
    except :
        import sys, traceback
        traceback.print_exc( file = sys.stderr )

        pass

    return False


#------------------------------------------------------------------------------------------
def upload_items( the_number_threads, the_file_bucket, the_file_api_version, the_working_dir, the_printing_depth ) :
    "Uploading file items"
    while True :
        a_dir_contents = os.listdir( the_working_dir )

        a_number_threads = max( min( the_number_threads, len( a_dir_contents ) ), 1 )
        print_d( "a_number_threads = %d\n" % a_number_threads, the_printing_depth )

        a_worker_pool = WorkerPool( a_number_threads )
        
        a_dir_contents.sort()
        a_dir_contents.reverse()
        
        a_file_bucket_names = [ an_item_key.name for an_item_key in the_file_bucket.list() ]
        
        for a_file_item in a_dir_contents :
            a_file_path = os.path.join( the_working_dir, a_file_item )
            print_d( "'%s'\n" % a_file_path, the_printing_depth + 1 )
        
            if a_file_item in a_file_bucket_names :
                os.remove( a_file_path )

                continue

            a_worker_pool.charge( upload_item, ( a_file_item, a_file_path, the_file_bucket, the_file_api_version, the_printing_depth + 2 ) )

            pass

        a_worker_pool.shutdown()
        an_is_all_right = a_worker_pool.is_all_right()

        if an_is_all_right :
            mark_finished( the_working_dir, the_file_bucket, the_printing_depth )

            break

        pass

    return True


#------------------------------------------------------------------------------------------
def upload_file( the_s3_conn, the_number_threads, the_study_file_key, the_study_id, the_printing_depth ) :
    a_file_api_version = extract_api_version( the_study_file_key )
    a_hex_md5, a_file_path = extract_file_props( the_study_file_key.name, a_file_api_version )

    a_working_dir = generate_uploading_dir( a_file_path )
    if not os.path.exists( a_working_dir ) :
        return True

    print_d( "the_study_file_key = %s\n" % the_study_file_key, the_printing_depth )
    print_d( "a_working_dir = '%s'\n" % a_working_dir, the_printing_depth )

    a_file_api_version = extract_api_version( the_study_file_key )
    print_d( "a_file_api_version = '%s'\n" % a_file_api_version, the_printing_depth )

    a_file_id, a_file_bucket_name = generate_id( the_study_id, the_study_file_key.name, a_file_api_version )
    print_d( "a_file_id = '%s'\n" % a_file_id, the_printing_depth )

    a_file_bucket = the_s3_conn.get_bucket( a_file_bucket_name )
    print_d( "a_file_bucket = %s\n" % a_file_bucket, the_printing_depth )

    return upload_items( the_number_threads, a_file_bucket, a_file_api_version, a_working_dir, the_printing_depth + 1 )


#------------------------------------------------------------------------------------------
def upload_files( the_s3_conn, the_number_threads, the_study_bucket, the_study_id, the_printing_depth ) :
    for a_study_file_key in the_study_bucket.list() :
        upload_file( the_s3_conn, the_number_threads, a_study_file_key, the_study_id, the_printing_depth )
        
        pass

    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --study-name='my interrupted study'"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += amazon.add_timeout_usage_description()
an_usage_description += amazon.add_threading_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--study-name",
                            metavar = "< an unique name of the user study >",
                            action = "store",
                            dest = "study_name" )
common.add_parser_options( a_option_parser )
amazon.add_parser_options( a_option_parser )
amazon.add_timeout_options( a_option_parser )
amazon.add_threading_parser_options( a_option_parser )
    
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

a_study_name = an_options.study_name
if a_study_name == None :
    a_study_name = raw_input()
    pass

print_d( "a_study_name = '%s'\n" % a_study_name )
    
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

a_number_threads = amazon.extract_threading_options( an_options, a_option_parser )

amazon.extract_timeout_options( an_options, a_option_parser )


print_i( "--------------------------- Connecting to Amazon S3 -----------------------------\n" )
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )


print_i( "--------------------------- Looking for study root ------------------------------\n" )
a_canonical_user_id = a_s3_conn.get_canonical_user_id()
print_d( "a_canonical_user_id = '%s'\n" % a_canonical_user_id )

a_root_bucket_name = hashlib.md5( a_canonical_user_id ).hexdigest()
a_root_bucket = a_s3_conn.get_bucket( a_root_bucket_name )
print_d( "a_root_bucket = %s\n" % a_root_bucket )


print_i( "--------------------------- Looking for study key -------------------------------\n" )
a_study_key = Key( a_root_bucket )
a_study_key.key = '%s' % ( a_study_name )
a_study_api_version = extract_api_version( a_study_key )
print_d( "a_study_api_version = '%s'\n" % a_study_api_version )


print_i( "----------------------- Looking for the appointed study -------------------------\n" )
a_canonical_user_id = a_s3_conn.get_canonical_user_id()

a_study_id, a_study_bucket_name = generate_id( a_canonical_user_id, a_study_name, a_study_api_version )
print_d( "a_study_id = '%s'\n" % a_study_id )

a_study_bucket = a_s3_conn.get_bucket( a_study_bucket_name )
print_d( "a_study_bucket = '%s'\n" % a_study_bucket )


print_i( "---------------------------- Uploading study files ------------------------------\n" )
a_data_loading_time = Timer()

upload_files( a_s3_conn, a_number_threads, a_study_bucket, a_study_id, 0 )

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_i( "-------------------------------------- OK ---------------------------------------\n" )
print a_study_name


#------------------------------------------------------------------------------------------
