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
from balloon.common import print_d, init_printing, print_i, print_e, sh_command, ssh_command, Timer, Worker

import balloon.amazon as amazon

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
def download_item( the_item_key, the_file_path, the_printing_depth ) :
    the_item_key.get_contents_to_filename( the_file_path )
    print_d( "an_item_key = %s\n" % the_item_key, the_printing_depth )
        
    pass


#------------------------------------------------------------------------------------------
class DownloadItem :
    def __init__( self, the_item_key, the_file_path, the_printing_depth ) :
        self.item_key = the_item_key
        self.file_path = the_file_path
        self.printing_depth = the_printing_depth

        pass
    
    def run( self ) :
        download_item( self.item_key, self.file_path, self.printing_depth )

        return self

    pass


#------------------------------------------------------------------------------------------
def download_items( the_worker, the_number_threads, the_file_bucket, the_file_basename, the_output_dir, the_printing_depth ) :
    a_worker = Worker( the_number_threads )

    import tempfile
    a_working_dir = tempfile.mkdtemp( dir = the_output_dir )
    a_working_dir = os.path.join( the_output_dir, a_working_dir )
    print_d( "a_working_dir = '%s'\n" % a_working_dir, the_printing_depth )

    a_wait = 1
    import time, random
    an_is_everything_uploaded = False
    while not an_is_everything_uploaded :
        for an_item_key in the_file_bucket.get_all_keys() :
            if an_item_key.name == the_file_bucket.name :
                an_is_everything_uploaded = True
                continue

            a_file_path = os.path.join( a_working_dir, an_item_key.name )
            if os.path.exists( a_file_path ) :
                continue

            print_d( "a_file_path = %s\n" % a_file_path, the_printing_depth )

            a_task = DownloadItem( an_item_key, a_file_path, the_printing_depth + 1 )
            
            a_worker.put( a_task )
            
            pass

        a_worker.join()

        # Exponential backoff
        a_wait = a_wait * 2 
        a_sleep = a_wait * random.random()
        time.sleep( a_sleep )

        pass
    
    the_worker.status = a_worker.status

    sh_command( "cd '%s' && cat %s.tgz-* | tar -xzf - -C '%s'" % 
                ( a_working_dir, the_file_basename, the_output_dir ), 
                the_printing_depth )

    import shutil
    shutil.rmtree( a_working_dir, True )
    
    pass


#------------------------------------------------------------------------------------------
def download_file( the_worker, the_number_threads, the_s3_conn, the_study_file_key, the_study_id, the_output_dir, the_printing_depth ) :
    a_file_name = the_study_file_key.key.split( ':' )[ 0 ]
    a_file_dirname = os.path.dirname( a_file_name )
    a_file_basename = os.path.basename( a_file_name )

    print_d( "the_study_file_key = %s\n" % the_study_file_key, the_printing_depth )

    a_file_id = '%s/%s' % ( the_study_id, the_study_file_key.key )
    print_d( "a_file_id = '%s'\n" % a_file_id, the_printing_depth )

    a_file_bucket_name = hashlib.md5( a_file_id ).hexdigest()

    a_file_bucket = the_s3_conn.get_bucket( a_file_bucket_name )
    print_d( "a_file_bucket = %s\n" % a_file_bucket, the_printing_depth )

    download_items( the_worker, the_number_threads, a_file_bucket, a_file_basename, the_output_dir, the_printing_depth + 1 )
        
    pass


#------------------------------------------------------------------------------------------
class DownloadFile :
    def __init__( self, the_worker, the_number_threads, the_s3_conn, the_study_file_key, the_study_id, the_output_dir, the_printing_depth ) :
        self.worker = the_worker
        self.number_threads = the_number_threads
        self.s3_conn = the_s3_conn
        self.study_file_key = the_study_file_key
        self.study_id = the_study_id
        self.output_dir = the_output_dir
        self.printing_depth = the_printing_depth

        pass
    
    def run( self ) :
        download_file( self.worker, self.number_threads, self.s3_conn, self.study_file_key, self.study_id, self.output_dir, self.printing_depth )

        return self

    pass


#------------------------------------------------------------------------------------------
def download_files( the_worker, the_number_threads, the_s3_conn, the_study_file_keys, the_study_id, the_output_dir, the_printing_depth ) :
    for a_study_file_key in the_study_file_keys :
        a_task = DownloadFile( the_worker, the_number_threads, the_s3_conn, a_study_file_key, the_study_id, the_output_dir, the_printing_depth )
        
        the_worker.put( a_task )
        
        pass

    the_worker.join()

    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --study-name='my uploaded study' --output-dir='./tmp'"
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
                            dest = "study_name",
                            help = "(intialized from input, otherwise)" )
a_option_parser.add_option( "--output-dir",
                            metavar = "< location of the task defintion >",
                            action = "store",
                            dest = "output_dir",
                            help = "(the same a 'study' name, by default)" )
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
    
an_output_dir = an_options.output_dir
if an_output_dir == None :
    an_output_dir = os.path.join( an_engine_dir, a_study_name )
    pass

import shutil
shutil.rmtree( an_output_dir, True )
os.makedirs( an_output_dir )

print_d( "an_output_dir = '%s'\n" % an_output_dir )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

a_number_threads = amazon.extract_threading_options( an_options, a_option_parser )

amazon.extract_timeout_options( an_options, a_option_parser )


print_i( "--------------------------- Connecting to Amazon S3 -----------------------------\n" )
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )

a_canonical_user_id = a_s3_conn.get_canonical_user_id()
print_d( "a_canonical_user_id = '%s'\n" % a_canonical_user_id )


print_i( "------------------------ Looking for the study bucket ---------------------------\n" )
a_study_id = '%s/%s' % ( a_canonical_user_id, a_study_name )
a_study_bucket_name = hashlib.md5( a_study_id ).hexdigest()

a_study_bucket = None
try :
    a_study_bucket = a_s3_conn.get_bucket( a_study_bucket_name )
except :
    print_e( "There is no study with such name ('%s')\n" % a_study_name )
    pass

print_d( "a_study_bucket = '%s'\n" % a_study_bucket.name )


print_i( "--------------------------- Reading the study files -----------------------------\n" )
a_data_loading_time = Timer()

a_study_file_keys = a_study_bucket.get_all_keys()
a_worker = Worker( len( a_study_file_keys ) )

download_files( a_worker, a_number_threads, a_s3_conn, a_study_file_keys, a_study_id, an_output_dir, 0 )

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_i( "-------------------------------------- %s ---------------------------------------\n" % a_worker.status )

