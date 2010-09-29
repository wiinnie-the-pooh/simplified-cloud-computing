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
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, Timer

from balloon import amazon
from balloon.amazon import ec2 as amazon_ec2


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --image-location='us-east-1' --reservation-id='r-8cc1dfe7' --identity-file='~/.ssh/tmpaSRNcY.pem'"
an_usage_description += amazon.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

an_option_parser.add_option( "--image-location",
                             metavar = "< location of the AMI >",
                             action = "store",
                             dest = "image_location",
                             help = "(\"%default\", by default)",
                             default = None )
an_option_parser.add_option( "--reservation-id",
                             metavar = "< Amazon EC2 Reservation ID >",
                             action = "store",
                             dest = "reservation_id",
                             help = "(\"%default\", by default)",
                             default = None )
an_option_parser.add_option( "--identity-file",
                             metavar = "< selects a file from which the identity (private key) for RSA or DSA authentication is read >",
                             action = "store",
                             dest = "identity_file",
                             default = None )
amazon.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

an_image_location = an_options.image_location
if an_image_location == None :
    an_image_location = raw_input()
    pass

a_reservation_id = an_options.reservation_id
if a_reservation_id == None :
    a_reservation_id = raw_input()
    pass

an_identity_file = an_options.identity_file
if an_identity_file == None :
    an_identity_file = raw_input()
    pass
import os.path
an_identity_file = os.path.expanduser( an_identity_file )
an_identity_file = os.path.abspath( an_identity_file )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys
an_engine = sys.argv[ 0 ]

a_call = "%s  --image-location='%s' --reservation-id='%s' --identity-file='%s' %s" % \
    ( an_engine, an_image_location, a_reservation_id, an_identity_file, amazon.compose_call( an_options ) )
print_d( a_call + '\n' )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
a_spent_time = Timer()

an_ec2_conn = amazon_ec2.region_connect( an_image_location, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

a_reservation = amazon_ec2.get_reservation( an_ec2_conn, a_reservation_id )
print_d( 'a_reservation.instances = %s\n' % a_reservation.instances )


print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
print a_reservation.region.name
print a_reservation.id


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
print_d( a_call + '\n' )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
