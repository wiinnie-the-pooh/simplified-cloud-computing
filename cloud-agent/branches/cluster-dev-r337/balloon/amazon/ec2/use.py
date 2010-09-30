

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
    return " --image-location='us-east-1' --reservation-id='r-8cc1dfe7' --identity-file='~/.ssh/tmpaSRNcY.pem' --host-port=22 --login-name='ubuntu'"


#--------------------------------------------------------------------------------------
def add_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--image-location",
                                  metavar = "< location of the AMI >",
                                  action = "store",
                                  dest = "image_location",
                                  help = "(\"%default\", by default)",
                                  default = None )
    the_option_parser.add_option( "--reservation-id",
                                  metavar = "< Amazon EC2 Reservation ID >",
                                  action = "store",
                                  dest = "reservation_id",
                                  help = "(\"%default\", by default)",
                                  default = None )
    the_option_parser.add_option( "--identity-file",
                                  metavar = "< selects a file from which the identity (private key) for RSA or DSA authentication is read >",
                                  action = "store",
                                  dest = "identity_file",
                                  default = None )
    the_option_parser.add_option( "--host-port",
                                  metavar = "< port to be used >",
                                  type = "int",
                                  action = "store",
                                  dest = "host_port",
                                  default = None )
    the_option_parser.add_option( "--login-name",
                                  metavar = "< specifies the user to log in as on the remote machine >",
                                  action = "store",
                                  dest = "login_name",
                                  help = "(\"%default\", by default)",
                                  default = 'ubuntu' )
    pass


#--------------------------------------------------------------------------------------
def unpuck( the_options ) :
    an_image_location = the_options.image_location
    a_reservation_id = the_options.reservation_id
    an_identity_file = the_options.identity_file
    a_host_port = the_options.host_port
    a_login_name = the_options.login_name

    return an_image_location, a_reservation_id, an_identity_file, a_host_port, a_login_name


#--------------------------------------------------------------------------------------
def compose_call( the_options ) :
    an_image_location, a_reservation_id, an_identity_file, a_host_port, a_login_name = unpuck( the_options )

    a_call = "--image-location='%s' --reservation-id='%s' --identity-file='%s' --host-port=%d --login-name='%s'" % \
        ( an_image_location, a_reservation_id, an_identity_file, a_host_port, a_login_name )
    
    return a_call


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    an_image_location = the_options.image_location
    if an_image_location == None :
        an_image_location = raw_input()
        pass

    a_reservation_id = the_options.reservation_id
    if a_reservation_id == None :
        a_reservation_id = raw_input()
        pass
    
    an_identity_file = the_options.identity_file
    if an_identity_file == None :
        an_identity_file = raw_input()
        pass
    import os.path
    an_identity_file = os.path.expanduser( an_identity_file )
    an_identity_file = os.path.abspath( an_identity_file )
    
    a_host_port = the_options.host_port
    if a_host_port == None :
        a_host_port = int( raw_input() )
        pass
    
    a_login_name = the_options.login_name
    
    return an_image_location, a_reservation_id, an_identity_file, a_host_port, a_login_name


#--------------------------------------------------------------------------------------
def get_reservation( the_ec2_conn, the_reservation_id ) :
    for a_reservation in the_ec2_conn.get_all_instances() :
        if a_reservation.id == the_reservation_id :
            return a_reservation
        pass
    pass


#--------------------------------------------------------------------------------------
