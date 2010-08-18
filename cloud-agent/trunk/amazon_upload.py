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
This script is responsible for efficient uploading of multi source data
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, ssh_command, Timer

import balloon.amazon as amazon
import boto

import sys, os, os.path, uuid, hashlib


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --study-name='my favorite study'"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += " <source 1> <source 2> ..."

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
    
a_sources = list()
for an_arg in an_args :
    if not os.path.exists( an_arg ) :
        print_e( "The given source should exists\n" )
        pass
    a_sources.append( os.path.abspath( an_arg ) )
    pass

print_d( "a_sources = %r\n" % a_sources )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


print_d( "\n---------------------------------------------------------------------------\n" )
import boto
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )
print_d( "a_s3_conn.get_canonical_user_id() = %s\n" % a_s3_conn.get_canonical_user_id() )

a_bucket_name = hashlib.md5( a_study_name ).hexdigest()
a_s3_bucket = a_s3_conn.create_bucket( a_bucket_name )
print_d( "a_s3_bucket.name = '%s'\n" % a_s3_bucket.name )


print_d( "\n---------------------------------------------------------------------------\n" )
print_d( 'OK\n' )


#--------------------------------------------------------------------------------------
