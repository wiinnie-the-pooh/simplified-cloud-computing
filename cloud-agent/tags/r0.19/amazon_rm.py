#!/usr/bin/env python

#------------------------------------------------------------------------------------------
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
Removes whole appointed cloud study or just given files from this study
"""

#------------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command, ssh_command
from balloon.common import generate_id, generate_file_key, generate_item_key
from balloon.common import extract_file_props, extract_item_props
from balloon.common import study_api_version, file_api_version
from balloon.common import Timer, WorkerPool, compute_md5

import balloon.amazon as amazon
from balloon.amazon import mark_api_version, extract_api_version

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
def rm_items( the_file_bucket, the_printing_depth ) :
    "Removing the file items"
    for an_item_key in the_file_bucket.list() :
        print_d( "'%s' - %s\n" % ( an_item_key.name, an_item_key ), the_printing_depth )

        an_item_key.delete()

        pass

    pass


#------------------------------------------------------------------------------------------
def rm_file( the_file_key, the_study_id, the_printing_depth ) :
    "Reading the study files"
    a_file_api_version = extract_api_version( the_file_key )
    print_d( "'%s' - '%s' - " % ( the_file_key.name, a_file_api_version), the_printing_depth )
        
    a_file_id, a_file_bucket_name = generate_id( the_study_id, the_file_key.name, a_file_api_version )
    a_file_bucket_name = hashlib.md5( a_file_id ).hexdigest()
        
    a_file_bucket = a_s3_conn.get_bucket( a_file_bucket_name )
    print_d( "%s\n" % a_file_bucket )

    rm_items( a_file_bucket, the_printing_depth + 1 )
        
    a_file_bucket.delete()

    the_file_key.delete()

    pass


#------------------------------------------------------------------------------------------
def rm_files( the_study_bucket, the_study_id, the_printing_depth ) :
    "Reading the study files"
    for a_file_key in the_study_bucket.list() :
        rm_file( a_file_key, the_study_id, the_printing_depth )
        
        pass

    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface
an_usage_description = "%prog"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += amazon.add_timeout_usage_description()
an_usage_description += amazon.add_threading_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
common.add_parser_options( a_option_parser, True )
amazon.add_parser_options( a_option_parser )
amazon.add_timeout_options( a_option_parser )
amazon.add_threading_parser_options( a_option_parser )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

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
a_root_bucket = None
try :
    a_root_bucket = a_s3_conn.get_bucket( a_root_bucket_name )
except :
    print_e( "Can not find user's study root" )
    pass

print_d( "a_root_bucket = %s\n" % a_root_bucket )

if len( an_args ) == 0 :
    print_e( "You need to give a study name, at least, to perform this command" )
    pass

a_study_name = an_args[ 0 ]

print_i( "--------------------------- Looking for study key -------------------------------\n" )
a_study_key = Key( a_root_bucket )
a_study_key.key = '%s' % ( a_study_name )
a_study_api_version = extract_api_version( a_study_key )
print_d( "a_study_api_version = '%s'\n" % a_study_api_version )

print_i( "----------------------- Looking for the appointed study -------------------------\n" )
a_study_id, a_study_bucket_name = generate_id( a_canonical_user_id, a_study_name, a_study_api_version )
print_d( "a_study_id = '%s'\n" % a_study_id )

a_study_bucket = a_s3_conn.get_bucket( a_study_bucket_name )
print_d( "a_study_bucket = '%s'\n" % a_study_bucket )

print_i( "-------------------------- Removing study files -----------------------------\n" )
if len( an_args ) == 1 :
    rm_files( a_study_bucket, a_study_id, 0 )

    print_i( "------------------------------- Removing study ----------------------------------\n" )
    a_study_bucket.delete()
    a_study_key.delete()

else :
    for an_arg in an_args[ 1 : ] :
        a_file_name = an_arg
        a_file_key = Key( a_study_bucket )
        a_file_key.key = '%s' % ( a_study_name )

        rm_file( a_file_key, a_study_id, 0 )

        pass

    pass

print_i( "-------------------------------------- OK ---------------------------------------\n" )
