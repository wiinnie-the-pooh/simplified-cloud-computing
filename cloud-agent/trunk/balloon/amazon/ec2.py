

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
from balloon.common import print_e, print_d, ssh_command, Timer

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
                                  default = "ami-2d4aa444" ) # ami-fd4aa494
    
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
                                  action = "store",
                                  dest = "min_count",
                                  help = "(\"%default\", by default)",
                                  default = "1" )
    
    the_option_parser.add_option( "--max-count",
                                  metavar = "< minimum number of instances to start >",
                                  action = "store",
                                  dest = "max_count",
                                  help = "(\"%default\", by default)",
                                  default = "1" )
    
    the_option_parser.add_option( "--user-name",
                                  metavar = "< SSH connection user name >",
                                  action = "store",
                                  dest = "user_name",
                                  help = "(\"%default\", by default)",
                                  default = "ubuntu" )

    pass


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    an_image_id = the_options.image_id
    an_image_location = the_options.image_location
    an_instance_type = the_options.instance_type
    a_min_count = the_options.min_count
    a_max_count = the_options.max_count
    a_user_name = the_options.user_name

    return an_image_id, an_image_location, an_instance_type, a_min_count, a_max_count, a_user_name


#--------------------------------------------------------------------------------------
def wait_ssh( the_ssh_connect, the_ssh_client, the_command ) :
    print_d( "ssh'ing " )
    while True :
        try :
            print_d( '.' )
            the_ssh_connect()
            ssh_command( the_ssh_client, 'echo  > /dev/null' )
            break
        except :
            continue
        pass

    pass


#--------------------------------------------------------------------------------------
def wait_activation( the_instance, the_ssh_connect, the_ssh_client ) :
    while True :
        try :
            print_d( '%s ' % the_instance.update() )
            break
        except :
            continue
        pass
    
    # Making sure that corresponding instances are ready to use
    while True :
        try :
            if the_instance.update() == 'running' :
                break
            print_d( '.' )
        except :
            continue
        pass
    
    print_d( ' %s\n' % the_instance.update() )

    wait_ssh( the_ssh_connect, the_ssh_client, 'echo  > /dev/null' )

    pass


#--------------------------------------------------------------------------------------
def run_instance( the_image_id, the_image_location, the_instance_type, 
                  the_min_count, the_max_count, 
                  the_user_name, the_aws_access_key_id, the_aws_secret_access_key ) :
    print_d( "\n-------------------------- Defining image location ------------------------\n" )
    an_instance_reservation_time = Timer()

    # Establish an connection with EC2
    import boto.ec2
    a_regions = boto.ec2.regions()
    print_d( 'a_regions = %r\n' % a_regions )

    an_image_region = None
    for a_region in a_regions :
        if a_region.name == the_image_location :
            an_image_region = a_region
            pass
        pass

    if an_image_region == None :
        print_e( "There no region with such location - '%s'\n" % an_image_region )
        pass

    print_d( 'an_image_region = < %r >\n' % an_image_region )

    an_ec2_conn = an_image_region.connect( aws_access_key_id = the_aws_access_key_id, 
                                           aws_secret_access_key = the_aws_secret_access_key )
    print_d( 'an_ec2_conn = < %r >\n' % an_ec2_conn )

    an_images = an_ec2_conn.get_all_images( image_ids = the_image_id )
    an_image = an_images[ 0 ]
    print_d( 'an_image = < %s >\n' % an_image )


    print_d( "\n---------------- Creating unique key-pair and security group --------------\n" )
    import tempfile
    an_unique_file = tempfile.mkstemp()[ 1 ]
    an_unique_name = os.path.basename( an_unique_file )
    os.remove( an_unique_file )
    print_d( "an_unique_name = '%s'\n" % an_unique_name )

    # Asking EC2 to generate a new ssh "key pair"
    a_key_pair_name = an_unique_name
    a_key_pair = an_ec2_conn.create_key_pair( a_key_pair_name )
    
    # Saving the generated ssh "key pair" locally
    a_key_pair_dir = os.path.expanduser( "~/.ssh")
    a_key_pair.save( a_key_pair_dir )
    a_key_pair_file = os.path.join( a_key_pair_dir, a_key_pair.name ) + os.path.extsep + "pem"
    print_d( "a_key_pair_file = '%s'\n" % a_key_pair_file )

    import stat
    os.chmod( a_key_pair_file, stat.S_IRUSR )

    # Asking EC2 to generate a new "sequirity group" & apply corresponding firewall permissions
    a_security_group = an_ec2_conn.create_security_group( an_unique_name, 'temporaly generated' )
    a_security_group.authorize( 'tcp', 80, 80, '0.0.0.0/0' )
    a_security_group.authorize( 'tcp', 22, 22, '0.0.0.0/0' )
    
    
    print_d( "\n---------------------------- Running actual image -------------------------\n" )
    # Creating a EC2 "reservation" with all the parameters mentioned above
    a_reservation = an_image.run( instance_type = the_instance_type, min_count = the_min_count, max_count = the_max_count, 
                                  key_name = a_key_pair_name, security_groups = [ a_security_group.name ] )
    an_instance = a_reservation.instances[ 0 ]
    print_d( 'a_reservation.instances = %s\n' % a_reservation.instances )


    print_d( "\n-------------- Instantiating ssh connection with root access --------------\n" )
    # Instantiating ssh connection with root access
    import paramiko
    a_ssh_client = paramiko.SSHClient()
    a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    a_rsa_key = paramiko.RSAKey( filename = a_key_pair_file )

    a_ssh_connect = lambda : a_ssh_client.connect( hostname = an_instance.dns_name, port = 22, username = the_user_name, pkey = a_rsa_key )

    # Making sure that corresponding instances are ready to use
    wait_activation( an_instance, a_ssh_connect, a_ssh_client )
    print_d( 'ssh -i %s %s@%s\n' % ( a_key_pair_file, the_user_name, an_instance.dns_name ) )

    print_d( "an_instance_reservation_time = %s, sec\n" % an_instance_reservation_time )


    # print_d( "\n----------------------- Additional customization steps --------------------\n" )
    # ssh_command( a_ssh_client, """sudo cat /etc/ssh/ssh_config""" )
    # ssh_command( a_ssh_client, """sudo sh -c 'echo "\n    ClientAliveInterval 10\n    Port 22" >> /etc/ssh/ssh_config'""" )
    # ssh_command( a_ssh_client, """sudo cat /etc/ssh/ssh_config""" )
    # ssh_command( a_ssh_client, """sudo /etc/init.d/ssh restart""" )


    return an_instance, a_ssh_client


#--------------------------------------------------------------------------------------
