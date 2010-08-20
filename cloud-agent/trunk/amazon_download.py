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
from balloon.common import print_d, init_printing, print_i, print_e, sh_command, ssh_command, Timer

import balloon.amazon as amazon

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


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
                            help = "(intialized from input, otherwise)" )

a_option_parser.add_option( "--output-dir",
                            metavar = "< location of the task defintion >",
                            action = "store",
                            dest = "output_dir",
                            help = "(the same a 'study' name, by default)" )

common.add_parser_options( a_option_parser )

amazon.add_parser_options( a_option_parser )
    
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


print_d( "\n----------------------- Connecting to Amazon S3 ---------------------------\n" )
#------------------------------------------------------------------------------------------
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )

a_canonical_user_id = a_s3_conn.get_canonical_user_id()
print_d( "a_canonical_user_id = '%s'\n" % a_canonical_user_id )


print_d( "\n-------------------- Looking for the study bucket -------------------------\n" )
#------------------------------------------------------------------------------------------
a_study_id = '%s/%s' % ( a_canonical_user_id, a_study_name )
a_study_bucket_name = hashlib.md5( a_study_id ).hexdigest()

a_study_bucket = None
try :
    a_study_bucket = a_s3_conn.get_bucket( a_study_bucket_name )
except :
    print_e( "There is no study with such name ('%s')\n" % a_study_name )
    pass

print_d( "a_study_bucket = '%s'\n" % a_study_bucket.name )


print_i( "\n----------------------- Reading the study files ---------------------------\n" )
#------------------------------------------------------------------------------------------
for a_file_key in a_study_bucket.get_all_keys() :
    an_init_printing = init_printing()

    a_file_dirname = os.path.dirname( a_file_key.key )
    a_file_basename = os.path.basename( a_file_key.key )

    print_d( "a_file_key = %s\n" % a_file_key.key )

    a_file_id = '%s/%s' % ( a_study_id, a_file_key.key )
    print_d( "a_file_id = %s\n" % a_file_id )

    a_file_bucket_name = hashlib.md5( a_file_id ).hexdigest()

    a_file_bucket = a_s3_conn.get_bucket( a_file_bucket_name )
    print_d( "a_file_bucket = '%s'\n" % a_file_bucket.name )

    import tempfile
    a_working_dir = tempfile.mkdtemp( dir = an_output_dir )
    a_working_dir = os.path.join( an_output_dir, a_working_dir )
    print_d( "a_working_dir = %s\n" % a_working_dir )

    for an_item_key in a_file_bucket.get_all_keys() :
        an_init_printing2 = init_printing()

        a_file_path = os.path.join( a_working_dir, an_item_key.name )

        an_item_key.get_contents_to_filename( a_file_path )
        print_d( "an_item_key.name = %s\n" % an_item_key.name )
        
        pass

    sh_command( "cd '%s' && cat %s.tgz-* | tar -xzf - -C '%s'" % ( a_working_dir, a_file_basename, an_output_dir ) )

    import shutil
    shutil.rmtree( a_working_dir, True )
    print_d( "\n" )
    
    pass


print_d( "\n---------------------------------- OK -------------------------------------\n" )
#------------------------------------------------------------------------------------------

