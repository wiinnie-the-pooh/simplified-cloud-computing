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
Cleans all nodes from cloudservers and cloudfiles that correspond to defined rackspace account
"""

#------------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, init_printing, print_i, print_e, sh_command, ssh_command, Timer

import balloon.amazon as amazon

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
def read_items( the_file_bucket, the_printing_depth ) :
    "Reading the file items"
    for an_item_key in the_file_bucket.get_all_keys() :
        print_d( "'%s' - %s\n" % ( an_item_key.name, an_item_key ), the_printing_depth )

        pass

    pass


#------------------------------------------------------------------------------------------
def read_files( the_study_bucket, the_study_id, the_printing_depth ) :
    "Reading the study files"
    for a_file_key in the_study_bucket.get_all_keys() :
        print_d( "'%s' - " % a_file_key.name, the_printing_depth )
        
        a_file_id = '%s/%s' % ( the_study_id, a_file_key.key )
        a_file_bucket_name = hashlib.md5( a_file_id ).hexdigest()
        
        a_file_bucket = a_s3_conn.get_bucket( a_file_bucket_name )
        print_d( "%s\n" % a_file_bucket )

        read_items( a_file_bucket, the_printing_depth + 1 )

        pass
    
    pass


#------------------------------------------------------------------------------------------
def read_studies( the_root_bucket, the_canonical_user_id, the_printing_depth ) :
    "Reading the studies"
    for a_study_key in the_root_bucket.get_all_keys() :
        a_study_name = a_study_key.name
        print_d( "'%s' - " % a_study_name, the_printing_depth )

        a_study_id = '%s/%s' % ( the_canonical_user_id, a_study_name )
        a_study_bucket_name = hashlib.md5( a_study_id ).hexdigest()
    
        a_study_bucket = None
        try :
            a_study_bucket = a_s3_conn.get_bucket( a_study_bucket_name )
        except :
            print_d( "There is no study with such name ('%s')\n" % a_study_name, the_printing_depth )
            return
        
        print_d( "%s\n" % a_study_bucket )
    
        read_files( a_study_bucket, a_study_id, the_printing_depth + 1 )
    
        pass

    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface
an_usage_description = "%prog"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
common.add_parser_options( a_option_parser )
amazon.add_parser_options( a_option_parser )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

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
    print_e( "Can not find user's study root" )
    pass

print_d( "a_root_bucket = %s\n" % a_root_bucket )


print_i( "---------------------------- Reading the studies --------------------------------\n" )
#------------------------------------------------------------------------------------------
read_studies( a_root_bucket, a_canonical_user_id, 1 )


print_i( "-------------------------------------- OK ---------------------------------------\n" )
#------------------------------------------------------------------------------------------
