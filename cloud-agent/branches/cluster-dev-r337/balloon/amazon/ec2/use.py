

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
from balloon.common import print_e, print_d, Timer

import os, os.path


#--------------------------------------------------------------------------------------
def add_usage_description() :
    return " --image-id='ami-2d4aa444' --image-location='us-east-1' --instance-type='m1.small' --min-count=1 --max-count=1 --user-name='ubuntu'"


#--------------------------------------------------------------------------------------
def add_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--image-id",
                                  metavar = "< Amazon EC2 AMI ID >",
                                  action = "store",
                                  dest = "image_id",
                                  help = "(\"%default\", by default)",
                                  default = "ami-2231c44b" ) # ami-fd4aa494 (ami-2d4aa444)
    
    the_option_parser.add_option( "--image-location",
                                  metavar = "< location of the AMI >",
                                  action = "store",
                                  dest = "image_location",
                                  help = "(\"%default\", by default)",
                                  default = "us-east-1" )

    the_option_parser.add_option( "--instance-type",
                                  metavar = "< type of the instance in terms of EC2 >",
                                  action = "store",
                                  dest = "instance_type",
                                  help = "(\"%default\", by default)",
                                  default = "m1.small" ) # m1.large
    
    the_option_parser.add_option( "--min-count",
                                  metavar = "< minimum number of instances to start >",
                                  type = "int",
                                  action = "store",
                                  dest = "min_count",
                                  help = "(%default, by default)",
                                  default = 1 )
    
    the_option_parser.add_option( "--max-count",
                                  metavar = "< minimum number of instances to start >",
                                  type = "int",
                                  action = "store",
                                  dest = "max_count",
                                  help = "(%default, by default)",
                                  default = 1 )

    the_option_parser.add_option( "--host-port",
                                  metavar = "< port to be used for ssh >",
                                  type = "int",
                                  action = "store",
                                  dest = "host_port",
                                  default = 22 )
    pass


#--------------------------------------------------------------------------------------
def unpuck( the_options ) :
    an_image_id = the_options.image_id
    an_image_location = the_options.image_location
    an_instance_type = the_options.instance_type
    a_min_count = the_options.min_count
    a_max_count = the_options.max_count
    a_host_port = the_options.host_port

    return an_image_id, an_image_location, an_instance_type, a_min_count, a_max_count, a_host_port


#--------------------------------------------------------------------------------------
def compose_call( the_options ) :
    an_image_id, an_image_location, an_instance_type, a_min_count, a_max_count, a_host_port = unpuck( the_options )

    a_call = "--image-id='%s' --image-location='%s' --instance-type='%s' --min-count=%d --max-count=%d --host-port=%d" % \
        ( an_image_id, an_image_location, an_instance_type, a_min_count, a_max_count, a_host_port )
    
    return a_call


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    an_image_id = the_options.image_id
    an_image_location = the_options.image_location
    an_instance_type = the_options.instance_type

    a_min_count = the_options.min_count
    a_max_count = the_options.max_count
    if a_min_count > a_max_count :
        import math
        print_d( '--min-count=%d > --max-count=%d : --max-count will be corrected to %d' 
                 % ( a_min_count, a_max_count, a_min_count ) )
        the_options.max_count = a_max_count = a_min_count
        pass

    a_host_port = the_options.host_port

    return an_image_id, an_image_location, an_instance_type, a_min_count, a_max_count, a_host_port


#--------------------------------------------------------------------------------------
def get_reservation( the_ec2_conn, the_reservation_id ) :
    for a_reservation in the_ec2_conn.get_all_instances() :
        if a_reservation.id == the_reservation_id :
            return a_reservation
        pass
    pass


#--------------------------------------------------------------------------------------
