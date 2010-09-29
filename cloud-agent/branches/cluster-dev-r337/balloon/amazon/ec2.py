

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
def wait4activation( the_instance ) :
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

    pass


#--------------------------------------------------------------------------------------
def get_reservation( the_ec2_conn, the_reservation_id ) :
    for a_reservation in the_ec2_conn.get_all_instances() :
        if a_reservation.id == the_reservation_id :
            return a_reservation
        pass
    pass


#--------------------------------------------------------------------------------------
def region_connect( the_image_location, the_aws_access_key_id, the_aws_secret_access_key ) :
    import boto.ec2
    a_regions = boto.ec2.regions()
    print_d( 'a_regions = %s\n' % [ str( a_region.name ) for a_region in a_regions ] )

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

    return an_ec2_conn


#--------------------------------------------------------------------------------------
def run_reservation( the_image_id, the_image_location, the_instance_type, 
                     the_min_count, the_max_count, the_host_port,
                     the_aws_access_key_id, the_aws_secret_access_key ) :
    print_d( "\n-------------------------- Defining image location ------------------------\n" )
    an_instance_reservation_time = Timer()

    an_ec2_conn = region_connect( the_image_location, the_aws_access_key_id, the_aws_secret_access_key )

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
    if not os.path.exists( a_key_pair_dir ) :
        os.makedirs( a_key_pair_dir )
        pass
    a_key_pair.save( a_key_pair_dir )
    an_identity_file = os.path.join( a_key_pair_dir, a_key_pair.name ) + os.path.extsep + "pem"
    print_d( "an_identity_file = '%s'\n" % an_identity_file )

    import stat
    os.chmod( an_identity_file, stat.S_IRUSR )

    # Asking EC2 to generate a new "sequirity group" & apply corresponding firewall permissions
    a_security_group = an_ec2_conn.create_security_group( an_unique_name, 'temporaly generated' )
    a_security_group.authorize( 'tcp', the_host_port, the_host_port, '0.0.0.0/0' ) # ssh port
    
    
    print_d( "\n-------------------------------- Running image ----------------------------\n" )
    # Creating a EC2 "reservation" with all the parameters mentioned above
    a_reservation = an_image.run( instance_type = the_instance_type, min_count = the_min_count, max_count = the_max_count, 
                                  key_name = a_key_pair_name, security_groups = [ a_security_group.name ] )
    print_d( 'a_reservation.instances = %s\n' % a_reservation.instances )

    a_password = "" # No password
    an_identity_file = an_identity_file
    a_host_port = the_host_port
    a_login_name = 'ubuntu'

    for an_instance in a_reservation.instances :
        wait4activation( an_instance ) # Making sure that corresponding instances are ready to use

        a_host_name = an_instance.public_dns_name
        print_d( 'ssh -o "StrictHostKeyChecking no" -i %s -p %d %s@%s\n' % ( an_identity_file, a_host_port, a_login_name, a_host_name ) )
        
        # To provide automatic ssh connection
        from balloon.common import ssh
        a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
        a_sftp_client = a_ssh_client.open_sftp()

        an_upload_name = os.path.basename( an_identity_file )
        a_sftp_client.put( an_identity_file, an_upload_name )

        a_target_name = '${HOME}/.ssh/id_rsa'
        ssh.command( a_ssh_client, 'mv -f %s %s' % ( an_upload_name, a_target_name ) )
        ssh.command( a_ssh_client, 'chmod 600 %s' % ( a_target_name ) )

        pass

    # To list all available nodes in the cluster into special <machines> file
    a_reservation = get_reservation( an_ec2_conn, a_reservation.id )
    a_master_node = an_instance = a_reservation.instances[ 0 ]
    a_host_name = an_instance.public_dns_name

    from balloon.common import ssh
    a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    ssh.command( a_ssh_client, 'echo %s > .openmpi_machines' % ( an_instance.private_ip_address ) )
    a_security_group.authorize( 'tcp', 1, 65535, '%s/0' % an_instance.private_ip_address ) # mpi cluster ports

    for an_instance in a_reservation.instances[ 1 : ] :
        ssh.command( a_ssh_client, 'echo %s >> .openmpi_machines' % ( an_instance.private_ip_address ) )
        a_security_group.authorize( 'tcp', 1, 65535, '%s/0' % an_instance.private_ip_address ) # mpi cluster ports
        pass

    return a_reservation, an_identity_file


#--------------------------------------------------------------------------------------
