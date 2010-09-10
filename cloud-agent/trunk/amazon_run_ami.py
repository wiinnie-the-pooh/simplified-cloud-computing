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
from balloon.common import print_d, print_e, sh_command, ssh_command, Timer

import balloon.amazon as amazon
from balloon.amazon import run_instance


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --image-id='ami-2d4aa444' --image-location='us-east-1' --instance-type='m1.small' --user-name='ubuntu'"
# an_usage_description = "%prog --image-id='ami-fd4aa494' --image-location='us-east-1' --instance-type='m1.large' --user-name='ubuntu'"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--image-id",
                            metavar = "< Amazon EC2 AMI ID >",
                            action = "store",
                            dest = "image_id",
                            help = "(\"%default\", by default)",
                            default = "ami-2d4aa444" )

a_option_parser.add_option( "--image-location",
                            metavar = "< location of the AMI >",
                            action = "store",
                            dest = "image_location",
                            help = "(\"%default\", by default)",
                            default = "us-east-1" )

a_option_parser.add_option( "--instance-type",
                            metavar = "< type of the instance in terms of EC2 >",
                            action = "store",
                            dest = "instance_type",
                            help = "(\"%default\", by default)",
                            default = "m1.small" )

a_option_parser.add_option( "--min-count",
                            metavar = "< minimum number of instances to start >",
                            action = "store",
                            dest = "min_count",
                            help = "(\"%default\", by default)",
                            default = "1" )

a_option_parser.add_option( "--max-count",
                            metavar = "< minimum number of instances to start >",
                            action = "store",
                            dest = "max_count",
                            help = "(\"%default\", by default)",
                            default = "1" )

a_option_parser.add_option( "--user-name",
                            metavar = "< SSH connection user name >",
                            action = "store",
                            dest = "user_name",
                            help = "(\"%default\", by default)",
                            default = "ubuntu" )

common.add_parser_options( a_option_parser )

amazon.add_parser_options( a_option_parser )
    
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

an_image_id = an_options.image_id
an_image_location = an_options.image_location
an_instance_type = an_options.instance_type
a_min_count = an_options.min_count
a_max_count = an_options.max_count
a_user_name = an_options.user_name

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


print_d( "\n------------------------ Running actual functionality ---------------------\n" )
an_instance, a_ssh_client = run_instance( an_image_id, an_image_location, an_instance_type, 
                                          a_min_count, a_max_count, 
                                          a_user_name, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

print_d( "\n--------------------------- Closing SSH connection ------------------------\n" )
a_ssh_client.close()


print_d( "\n-------------------------------------- OK ---------------------------------\n" )

