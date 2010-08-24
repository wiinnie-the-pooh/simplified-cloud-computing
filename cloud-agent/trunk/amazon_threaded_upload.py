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
from balloon.common import print_d, init_printing, print_i, print_e, sh_command, ssh_command, Timer

import balloon.amazon as amazon

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
from Queue import Queue

class Worker( Queue ) :
    "Run all the registered tasks in parallel"
    def __init__( self, the_number_threads ) :
        "Reserve given number of threads to perform the tasks"
        Queue.__init__( self )
        from threading import Thread
        for an_id in range( the_number_threads ) :
            a_thread = Thread( target = self )
            a_thread.daemon = True

            a_thread.start()
            
            pass
        
        pass
    
    def __call__( self ) :
        "Real execution of a task"
        while True:
            a_task = self.get()

            a_task.run()

            self.task_done()

            pass

        pass

    pass


#------------------------------------------------------------------------------------------
def upload_item( the_file_item, the_working_dir, the_file_bucket, the_printing_depth ) :
    "Uploading file item"
    a_file_path = os.path.join( the_working_dir, the_file_item )
    print_d( "'%s'\n" % a_file_path, the_printing_depth )

    a_part_key = Key( the_file_bucket )
    a_part_key.key = the_file_item
    a_part_key.set_contents_from_filename( a_file_path )
    print_d( "%s\n" % a_part_key, the_printing_depth + 1 )

    pass


#------------------------------------------------------------------------------------------
class UploadItem :
    def __init__( self, the_file_item, the_working_dir, the_file_bucket, the_printing_depth ) :
        self.file_item = the_file_item
        self.working_dir = the_working_dir
        self.file_bucket = the_file_bucket
        self.printing_depth = the_printing_depth
        pass
    
    def run( self ) :
        upload_item( self.file_item, self.working_dir, self.file_bucket, self.printing_depth )

        return self

    pass


#------------------------------------------------------------------------------------------
def upload_items( the_file_bucket, the_file_dirname, the_file_basename, the_upload_item_size, the_printing_depth ) :
    "Uploading file items"
    import tempfile
    a_working_dir = tempfile.mkdtemp()

    a_file_item_target = os.path.join( a_working_dir, the_file_basename )
    sh_command( "cd '%s' &&  tar -czf - '%s' | split --bytes=%d --suffix-length=5 - %s.tgz-" % 
                ( the_file_dirname, the_file_basename, the_upload_item_size, a_file_item_target ), the_printing_depth )

    a_dir_contents = os.listdir( a_working_dir )

    a_worker = Worker( len( a_dir_contents ) )

    for a_file_item in a_dir_contents :
        a_task = UploadItem( a_file_item, a_working_dir, the_file_bucket, the_printing_depth + 1 )

        a_worker.put( a_task )

        pass

    a_worker.join()

    import shutil
    shutil.rmtree( a_working_dir, True )

    pass


#------------------------------------------------------------------------------------------
def upload_file( the_file, the_study_bucket, the_study_id, the_upload_item_size, the_printing_depth ) :
    a_file_dirname = os.path.dirname( the_file )
    a_file_basename = os.path.basename( the_file )

    a_study_file_key = Key( the_study_bucket )
    a_study_file_key.key = '%s/%s' % ( a_file_dirname, a_file_basename )
    a_study_file_key.set_contents_from_string( 'dummy' )
    print_d( "a_study_file_key = %s\n" % a_study_file_key, the_printing_depth )

    a_file_id = '%s%s' % ( the_study_id, a_study_file_key.name )
    a_file_bucket_name = hashlib.md5( a_file_id ).hexdigest()
    print_d( "a_file_id = '%s'\n" % a_file_id, the_printing_depth )
    
    a_file_bucket = a_s3_conn.create_bucket( a_file_bucket_name )
    print_d( "a_file_bucket = %s\n" % a_file_bucket, the_printing_depth )

    upload_items( a_file_bucket, a_file_dirname, a_file_basename, the_upload_item_size, the_printing_depth + 1 )
    
    pass


#------------------------------------------------------------------------------------------
class UploadFile :
    def __init__( self, the_file, the_study_bucket, the_study_id, the_upload_item_size, the_printing_depth ) :
        self.file = the_file
        self.study_bucket = the_study_bucket
        self.study_id = the_study_id
        self.upload_item_size = the_upload_item_size
        self.printing_depth = the_printing_depth
        pass
    
    def run( self ) :
        upload_file( self.file, self.study_bucket, self.study_id, self.upload_item_size, self.printing_depth )

        return self

    pass


#------------------------------------------------------------------------------------------
def upload_files( the_files, the_study_bucket, the_study_id, the_upload_item_size, the_printing_depth ) :
    a_worker = Worker( len( the_files ) )

    for a_file in the_files :
        a_task = UploadFile( a_file, the_study_bucket, the_study_id, the_upload_item_size, the_printing_depth )

        a_worker.put( a_task )

        pass

    a_worker.join()

    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --study-name='my favorite study'"
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
                            default = 1024000 )
common.add_parser_options( a_option_parser )
amazon.add_parser_options( a_option_parser )
    
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

a_study_name = an_options.study_name
print_d( "a_study_name = '%s'\n" % a_study_name )
    
a_files = list()
for an_arg in an_args :
    if not os.path.exists( an_arg ) :
        print_e( "The given file should exists\n" )
        pass
    a_files.append( os.path.abspath( an_arg ) )
    pass

if len( a_files ) == 0 :
    print_e( "You should define one valid 'file' at least\n" )
    pass

print_d( "a_files = %r\n" % a_files )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


print_i( "--------------------------- Connecting to Amazon S3 -----------------------------\n" )
#------------------------------------------------------------------------------------------
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )


print_i( "--------------------------- Looking for study root ------------------------------\n" )
#------------------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------------------
a_root_study_key = Key( a_root_bucket )
a_root_study_key.key = '%s' % ( a_study_name )
a_root_study_key.set_contents_from_string( 'dummy' )
print_d( "a_root_study_key = %s\n" % a_root_study_key )

a_study_id = '%s/%s' % ( a_canonical_user_id, a_study_name )
a_study_bucket_name = hashlib.md5( a_study_id ).hexdigest()
print_d( "a_study_id = '%s'\n" % a_study_id )

a_study_bucket = a_s3_conn.create_bucket( a_study_bucket_name )
print_d( "a_study_bucket = '%s'\n" % a_study_bucket )


print_i( "---------------------------- Uploading study files ------------------------------\n" )
#------------------------------------------------------------------------------------------
a_data_loading_time = Timer()

upload_files( a_files, a_study_bucket, a_study_id, an_options.upload_item_size, 1 )

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_i( "-------------------------------------- OK ---------------------------------------\n" )
#------------------------------------------------------------------------------------------
print a_study_name


#------------------------------------------------------------------------------------------
