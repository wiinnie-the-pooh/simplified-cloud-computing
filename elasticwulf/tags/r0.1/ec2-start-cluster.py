#!/usr/bin/env python

''' 
ec2-start_cluster.py

This script will start mpi nodes on Amazon EC2, change the configuration strings in EC2config.py to match your
AWS keys and desired cluster size.

Created by Peter Skomoroch on 2007-04-09.
Copyright (c) 2007 DataWrangling. All rights reserved.

#TODO fix command line parsing....

'''

import sys
import EC2
from EC2config import *
import getopt


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
    conn = EC2.AWSAuthConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    if IMAGE_ID:
        print "image",IMAGE_ID


    if globals().has_key("MASTER_IMAGE_ID"):
        print "master image",MASTER_IMAGE_ID

        print "----- starting master -----"
        master_response = conn.run_instances(imageId=MASTER_IMAGE_ID, minCount=1, maxCount=1, keyName= KEYNAME, instanceType=INSTANCE_TYPE )
        print master_response

        print "----- starting workers -----"
        instances_response = conn.run_instances(imageId=IMAGE_ID, minCount=max((DEFAULT_CLUSTER_SIZE-1)/2, 1), maxCount=DEFAULT_CLUSTER_SIZE-1, keyName= KEYNAME, instanceType=INSTANCE_TYPE )
        print instances_response
        # TODO: if the workers failed, what should we do about the master?


    else:
        print "----- starting cluster -----"
        cluster_size=DEFAULT_CLUSTER_SIZE 
        instances_response = conn.run_instances(imageId=IMAGE_ID, minCount=max(cluster_size/2,1), maxCount=max(cluster_size,1), keyName= KEYNAME, instanceType=INSTANCE_TYPE )
        # instances_response is a list: [["RESERVATION", reservationId, ownerId, ",".join(groups)],["INSTANCE", instanceId, imageId, dnsName, instanceState], [ "INSTANCE"etc])
        # same as "describe instance"

        print instances_response


if __name__ == "__main__":
    sys.exit(main())

