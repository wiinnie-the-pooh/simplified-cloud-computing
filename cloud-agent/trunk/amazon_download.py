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


#--------------------------------------------------------------------------------------
"""
This script is responsible for efficient downloading of multi file data
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, init_printing, print_e, sh_command, ssh_command, Timer

import balloon.amazon as amazon

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


#--------------------------------------------------------------------------------------
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

common.add_parser_options( a_option_parser )

amazon.add_parser_options( a_option_parser )
    
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )


#--------------------------------------------------------------------------------------
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


print_d( "\n======================= Creating a study bucket ===========================" )
print_d( "\n---------------------------------------------------------------------------\n" )
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )

a_canonical_user_id = a_s3_conn.get_canonical_user_id()
print_d( "a_canonical_user_id = '%s'\n" % a_canonical_user_id )

a_study_id = '%s/%s' % ( a_canonical_user_id, a_study_name )
a_bucket_name = hashlib.md5( a_study_id ).hexdigest()

try :
    a_s3_conn.get_bucket( a_bucket_name )
    print_e( "You already have a study with this name ('%s')\n" % a_study_name )
except :
    # import sys, traceback
    # traceback.print_exc( file = sys.stderr )
    pass

a_study_bucket = a_s3_conn.create_bucket( a_bucket_name )
print_d( "a_study_bucket = '%s'\n" % a_study_bucket.name )


print_d( "\n======================= Registering study files ===========================" )
print_d( "\n---------------------------------------------------------------------------\n" )

for a_file in a_files :
    an_init_printing = init_printing()

    a_file_dirname = os.path.dirname( a_file )
    a_file_basename = os.path.basename( a_file )

    a_file_key = Key( a_study_bucket )
    a_file_key.key = '%s/%s' % ( a_file_dirname, a_file_basename )
    a_file_key.set_contents_from_string( 'dummy' )
    print_d( "a_file_key = %s\n" % a_file_key.name )

    a_file_id = '%s/%s' % ( a_study_id, a_file_key.key )
    a_bucket_name = hashlib.md5( a_file_id ).hexdigest()

    a_file_bucket = a_s3_conn.create_bucket( a_bucket_name )
    print_d( "a_file_bucket = '%s'\n" % a_file_bucket.name )

    sh_command( "cd '%s' &&  tar -czf - '%s' | split --bytes=1024 --suffix-length=5 - %s.tgz-" % ( a_file_dirname, a_file_basename, a_file_basename ) )

    a_dir_contents = os.listdir( a_file_dirname )

    for a_file_item in a_dir_contents :
        an_init_printing2 = init_printing()

        if not a_file_item.startswith( "%s.tgz-" % a_file_basename ) :
            continue

        a_file_path = os.path.join( a_file_dirname, a_file_item )
        print_d( "a_file_item = %s\n" % a_file_path )

        a_part_key = Key( a_file_bucket )
        a_part_key.key = a_file_item
        a_part_key.set_contents_from_filename( a_file_path )
        print_d( "a_part_key = %s\n" % a_part_key.name )

        os.remove( a_file_item )

        pass

    pass


print_d( "\n================================== OK =====================================" )
print_d( "\n---------------------------------------------------------------------------\n" )
print a_study_name


#--------------------------------------------------------------------------------------