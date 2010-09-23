#!/usr/bin/env python

''' 
ec2-start_cluster.py

This script will start mpi nodes on Amazon EC2, change the configuration strings in EC2config.py to match your
AWS keys and desired cluster size.

Created by Peter Skomoroch on 2007-04-09.
Copyright (c) 2007 DataWrangling. All rights reserved.

#TODO fix command line parsing....

'''

import sys, os, getopt
from EC2config import *


help_message = '''
SYNOPSIS
   ec2-start_cluster 
   ec2-start_cluster  [-n DEFAULT_CLUSTER_SIZE] [-s INSTANCE_TYPE]
    #
DESCRIPTION
    ec2-start_cluster.py

    This script will start mpi nodes on Amazon EC2, change the configuration strings in EC2config.py to match your
    AWS keys and desired cluster size.
OPTIONS
   -n/--nodes       Used to specify number of nodes in the cluster
                          overides DEFAULT_CLUSTER_SIZE variable in EC2Config.py

   -s/--size        Used to specify the Amazon AMI image size used in launching the cluster, 'm1.large', or 'm1.xlarge'
                          overides the INSTANCE_TYPE parameter in EC2Config.py 
                          
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hons:v", ["help", "output="])
        except getopt.error, msg:
            raise Usage(msg)
    
        # option processing
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-o", "--output"):
                output = value
            if option in ("-n", "--nodes"):
                DEFAULT_CLUSTER_SIZE = value
            if option in ("-s", "--size"):
                INSTANCE_TYPE = value               
                
        startcluster()      
    
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


def startcluster():
    from balloon.amazon.ec2 import wait4activation
    from balloon.common import print_d

    import boto
    conn = boto.connect_ec2()

    # Generating an unique name to be used for corresponding
    # ssh "key pair" & EC2 "security group"
    import tempfile
    an_unique_file = tempfile.mkstemp()[ 1 ]
    an_unique_name = os.path.basename( an_unique_file )
    os.remove( an_unique_file )
    print_d( 'an_unique_name = %s\n' % an_unique_name )
    
    # Asking EC2 to generate a new ssh "key pair"
    a_key_pair_name = an_unique_name
    a_key_pair = conn.create_key_pair( a_key_pair_name )
    
    # Saving the generated ssh "key pair" locally
    a_key_pair_dir = os.path.expanduser( "~/.ssh")
    a_key_pair.save( a_key_pair_dir )
    a_key_pair_file = os.path.join( a_key_pair_dir, a_key_pair.name ) + os.path.extsep + "pem"
    print_d( 'a_key_pair_file = %s\n' % a_key_pair_file )
    
    import stat
    os.chmod( a_key_pair_file, stat.S_IRUSR )

    # Asking EC2 to generate a new "sequirity group" & apply corresponding firewall permissions
    a_security_group = conn.create_security_group( an_unique_name, 'temporaly generated' )
    a_security_group.authorize( 'tcp', 80, 80, '0.0.0.0/0' )
    a_security_group.authorize( 'tcp', 22, 22, '0.0.0.0/0' )

    if IMAGE_ID:
        print "image",IMAGE_ID


    if globals().has_key("MASTER_IMAGE_ID"):
        print "master image",MASTER_IMAGE_ID

        print "----- starting master -----"
        an_image = conn.get_all_images( image_ids = MASTER_IMAGE_ID )[ 0 ]
        a_reservation = an_image.run( instance_type = INSTANCE_TYPE, 
                                      min_count = 1, max_count = 1, 
                                      key_name = a_key_pair_name, security_groups = [ a_security_group.name ] )
        an_instance = a_reservation.instances[ 0 ]
        wait4activation( an_instance )
        print an_instance

        print "----- starting workers -----"
        an_image = conn.get_all_images( image_ids = IMAGE_ID )[ 0 ]
        a_reservation = an_image.run( instance_type = INSTANCE_TYPE, 
                                      min_count = max((DEFAULT_CLUSTER_SIZE-1)/2, 1), max_count = DEFAULT_CLUSTER_SIZE-1, 
                                      key_name = a_key_pair_name, security_groups = [ a_security_group.name ] )
        for an_instance in a_reservation.instances :
            wait4activation( an_instance )
            print an_instance
            pass

        print a_reservation

        # TODO: if the workers failed, what should we do about the master?

    else:
        print "----- starting cluster -----"
        an_image = conn.get_all_images( image_ids = IMAGE_ID )[ 0 ]
        a_reservation = an_image.run( instance_type = 'm1.small', 
                                      min_count = max(DEFAULT_CLUSTER_SIZE/2,1), max_count = max(DEFAULT_CLUSTER_SIZE,1), 
                                      key_name = a_key_pair_name, security_groups = [ a_security_group.name ] )
        for an_instance in a_reservation.instances :
            wait4activation( an_instance )
            print an_instance
            pass

        print a_reservation


if __name__ == "__main__":
    sys.exit(main())

