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
This script is responsible for efficient downloading of multi file data
"""


#------------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command, ssh_command
from balloon.common import Timer, WorkerPool, compute_md5, generate_id

import balloon.amazon as amazon

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
def download_item( the_item_key, the_file_path, the_printing_depth ) :
    try :
        the_item_key.get_contents_to_filename( the_file_path )
        print_d( "an_item_key = %s\n" % the_item_key, the_printing_depth )
        
        return True
    except :
        import sys, traceback
        traceback.print_exc( file = sys.stderr )

        pass

    return False


#------------------------------------------------------------------------------------------
def download_items( the_number_threads, the_file_bucket, the_file_basename, the_output_dir, the_printing_depth ) :
    an_is_download_ok = False
    an_is_everything_uploaded = False
    while not an_is_everything_uploaded or not an_is_download_ok :
        a_worker_pool = WorkerPool( the_number_threads )

        for an_item_key in the_file_bucket.list() :
            if an_item_key.name == the_file_bucket.name :
                an_is_everything_uploaded = True
                continue

            a_file_name, a_hex_md5 = an_item_key.name.split( ':' )
            a_file_path = os.path.join( the_output_dir, a_file_name )

            if os.path.exists( a_file_path ) :
                a_file_pointer = open( a_file_path, 'rb' )
                a_md5 = compute_md5( a_file_pointer )[ 0 ]
                if a_hex_md5 == a_md5 :
                    continue

                os.remove( a_file_path )

                pass

            print_d( "a_file_path = %s\n" % a_file_path, the_printing_depth + 1 )

            a_worker_pool.charge( download_item, ( an_item_key, a_file_path, the_printing_depth + 2 ) )
            
            pass

        a_worker_pool.shutdown()
        an_is_download_ok = a_worker_pool.is_all_right()

        pass
    
    return True


#------------------------------------------------------------------------------------------
def download_file( the_number_threads, the_enable_fresh, the_s3_conn, the_study_file_key, the_study_id, the_output_dir, the_printing_depth ) :
    a_hex_md5, a_file_name, an_upload_dir = the_study_file_key.key.split( ':' )
    a_file_dirname = os.path.dirname( a_file_name )
    a_file_basename = os.path.basename( a_file_name )
    print_d( "a_file_name = '%s'\n" % a_file_name, the_printing_depth )

    an_output_dir = os.path.join( the_output_dir, a_file_dirname[ 1 : ] )
    print_d( "an_output_dir = '%s'\n" % an_output_dir, the_printing_depth )
    
    if the_enable_fresh :
        import shutil
        shutil.rmtree( an_output_dir, True )

        pass

    if not os.path.exists( an_output_dir ) :
        os.makedirs( an_output_dir )

        pass

    a_file_path = os.path.join( an_output_dir, a_file_basename )
    print_d( "a_file_path = '%s'\n" % a_file_path, the_printing_depth )
    if os.path.exists( a_file_path ) :
        print_d( "nothing to be done, already downloaded\n", the_printing_depth + 1 )

        return True

    print_d( "the_study_file_key = %s\n" % the_study_file_key, the_printing_depth )

    a_file_id, a_file_bucket_name = generate_id( the_study_id, the_study_file_key.key )
    print_d( "a_file_id = '%s'\n" % a_file_id, the_printing_depth )

    a_file_bucket = the_s3_conn.get_bucket( a_file_bucket_name )
    print_d( "a_file_bucket = %s\n" % a_file_bucket, the_printing_depth )

    while True :
        download_items( the_number_threads, a_file_bucket, a_file_basename, an_output_dir, the_printing_depth + 1 )
        
        an_archive_name = "%s.tgz" % a_file_basename

        sh_command( "cd '%s' && cat %s-* > %s" % ( an_output_dir, an_archive_name, an_archive_name ), the_printing_depth )

        an_archive_path = os.path.join( an_output_dir, an_archive_name )
        an_archive_pointer = open( an_archive_path, 'rb' )
        a_md5 = compute_md5( an_archive_pointer )[ 0 ]

        print_d( "'%s' - %s\n" % ( a_hex_md5, ( a_hex_md5 == a_md5 ) ), the_printing_depth )

        if a_hex_md5 == a_md5 :
            break

        pass

    sh_command( "tar -xzf '%s' -C '%s'" % ( an_archive_path, an_output_dir ), the_printing_depth )

    # sh_command( "cd '%s' && rm %s-*" % ( an_output_dir, an_archive_name ), the_printing_depth )

    # os.remove( an_archive_path )

    return True


#------------------------------------------------------------------------------------------
def download_files( the_number_threads, the_enable_fresh, the_s3_conn, the_study_bucket, the_study_id, the_output_dir, the_printing_depth ) :
    a_study_file_keys = the_study_bucket.get_all_keys()
    a_worker_pool = WorkerPool( len( a_study_file_keys ) )

    for a_study_file_key in the_study_bucket.list() :
        a_worker_pool.charge( download_file, ( the_number_threads, the_enable_fresh, the_s3_conn, a_study_file_key, the_study_id, the_output_dir, the_printing_depth ) )
        
        pass

    a_worker_pool.shutdown()
    a_worker_pool.join()

    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --study-name='my uploaded study' --file-name='/home/alexey' --output-dir='./tmp'"
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
                            metavar = "< a name of an uploaded study >",
                            action = "store",
                            dest = "study_name",
                            help = "(intialized from input, otherwise)" )
a_option_parser.add_option( "--file-name",
                            metavar = "< a of a file into uploaded study >",
                            action = "store",
                            dest = "file_name",
                            help = "(if missed, all the study files will be downloaded)" )
a_option_parser.add_option( "--output-dir",
                            metavar = "< location of the task defintion >",
                            action = "store",
                            dest = "output_dir",
                            help = "(the same a 'study' name, by default)" )
a_option_parser.add_option( "--enable-fresh",
                            action = "store_true",
                            dest = "enable_fresh",
                            help = "do not take into account previous downloads",
                            default = False )
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
    
an_enable_fresh = an_options.enable_fresh
print_d( "an_enable_fresh = %s\n" % an_enable_fresh )

an_output_dir = an_options.output_dir
if an_output_dir == None :
    an_output_dir = os.path.join( an_engine_dir, a_study_name )
    pass

print_d( "an_output_dir = '%s'\n" % an_output_dir )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

a_number_threads = amazon.extract_threading_options( an_options, a_option_parser )

print_d( "a_number_threads = %d\n" % a_number_threads )

amazon.extract_timeout_options( an_options, a_option_parser )


print_i( "--------------------------- Connecting to Amazon S3 -----------------------------\n" )
import logging
logging.basicConfig( filename = "boto.log", level = logging.DEBUG )

a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )

a_canonical_user_id = a_s3_conn.get_canonical_user_id()
print_d( "a_canonical_user_id = '%s'\n" % a_canonical_user_id )


print_i( "------------------------ Looking for the study bucket ---------------------------\n" )
a_study_id, a_study_bucket_name = generate_id( a_canonical_user_id, a_study_name )

a_study_bucket = None
try :
    a_study_bucket = a_s3_conn.get_bucket( a_study_bucket_name )
except :
    print_e( "There is no study with such name ('%s')\n" % a_study_name )
    pass

print_d( "a_study_bucket = '%s'\n" % a_study_bucket.name )


print_i( "--------------------------- Reading the study files -----------------------------\n" )
a_data_loading_time = Timer()

a_file_name = an_options.file_name
if a_file_name == None :
    download_files( a_number_threads, an_enable_fresh, a_s3_conn, a_study_bucket, a_study_id, an_output_dir, 0 )

else :
    for a_study_file_key in a_study_bucket.list() :
        a_file_key_name = a_study_file_key.key.split( ':' )[ 1 ]
        print_d( "a_file_key_name = '%s'\n" % a_file_key_name )

        if a_file_name == a_file_key_name :
            download_file( a_number_threads, an_enable_fresh, a_s3_conn, a_study_file_key, a_study_id, an_output_dir, 0 )

            pass

        pass

    pass

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_i( "-------------------------------------- OK ---------------------------------------\n" )

