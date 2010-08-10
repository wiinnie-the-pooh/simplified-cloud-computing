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
from balloon.common import print_d, print_e, sh_command, ssh_command

import balloon.amazon as amazon

import sys, os, os.path, uuid


#--------------------------------------------------------------------------------------
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
    

#--------------------------------------------------------------------------------------
if __name__ == '__main__' :
    #---------------------------------------------------------------------------
    # Extracting and verifying command-line arguments

    an_options, an_args = a_option_parser.parse_args()

    common.extract_options( an_options )

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


    #---------------------------------------------------------------------------
    import logging
    logging.basicConfig( filename = "boto.log", level = logging.DEBUG )

    import boto
    an_ec2_conn = boto.connect_ec2()
    print_d( '%r\n' % an_ec2_conn )

    an_images = an_ec2_conn.get_all_images( image_ids = "ami-2d4aa444" )
    an_image = an_images[ 0 ]
    print_d( '%s\n' % an_image.location )

    import uuid
    a_key_pair_name = 'id_rsa_%s' % str( uuid.uuid4() )
    a_key_pair = an_ec2_conn.create_key_pair( a_key_pair_name )

    a_reservation = an_image.run( min_count = 1, max_count = 1, key_name = a_key_pair_name )
    an_instance = a_reservation.instances[ 0 ]

    while an_instance.update() != 'running' :
        print_d( '%s\n' % an_instance.update() )
        pass


    #---------------------------------------------------------------------------
    an_ec2_conn.delete_key_pair( a_key_pair_name )
    a_reservation.stop_all()


    #---------------------------------------------------------------------------
    print_d( 'OK\n' )
    pass


#--------------------------------------------------------------------------------------