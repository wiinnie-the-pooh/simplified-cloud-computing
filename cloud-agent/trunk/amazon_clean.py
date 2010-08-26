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
Cleans all nodes from cloudservers and cloudfiles that correspond to defined rackspace account
"""

#--------------------------------------------------------------------------------------
import os
AWS_ACCESS_KEY_ID = os.getenv( "AWS_ACCESS_KEY_ID" )
AWS_SECRET_ACCESS_KEY = os.getenv( "AWS_SECRET_ACCESS_KEY" )


#--------------------------------------------------------------------------------------
import boto

import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command, ssh_command, Timer, Worker


#--------------------------------------------------------------------------------------
print "--------------- Delete S3 buckets ----------------"
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

a_s3_worker = Worker( 8 )

# First remove all the bucket keys
for a_bucket in a_s3_conn.get_all_buckets() :
    a_s3_bucket_keys = a_bucket.get_all_keys()
    print "'%s' : %d" % ( a_bucket.name, len( a_s3_bucket_keys ) )

    for a_s3_bucket_key in a_s3_bucket_keys :
        print "\t'%s'" % ( a_s3_bucket_key.name )
        a_s3_worker.charge( lambda the_s3_bucket_key : the_s3_bucket_key.delete(), [ a_s3_bucket_key ] )

        pass

    pass

a_s3_worker.join()
print

# Remove the bucket itself
for a_bucket in a_s3_conn.get_all_buckets() :
    print "'%s'" % ( a_bucket.name )
    a_s3_worker.charge( lambda the_s3_bucket : the_s3_bucket.delete(), [ a_bucket ] )

    pass

a_s3_worker.shutdown()
a_s3_worker.join()
print


#--------------------------------------------------------------------------------------
print "-------------- Delete EC2 instances --------------"
an_ec2_conn = boto.connect_ec2( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
for a_reservation in an_ec2_conn.get_all_instances() :
    # print "%s" % ( a_reservation )
    for an_instance in a_reservation.instances :
        a_status = an_instance.update()
        if a_status != 'terminated' :
            print "%s : %s : '%s'" % ( an_instance, a_status, an_instance.dns_name )
            an_instance.stop()
            pass
        pass
    a_reservation.stop_all()
    pass

print


print "-------------- Delete EC2 key pairs --------------"
for a_key_pair in an_ec2_conn.get_all_key_pairs() :
    print a_key_pair.name
    # an_ec2_conn.delete_key_pair( a_key_pair ) # Does not work (bug)
    a_key_pair.delete()

    a_key_pair_dir = os.path.expanduser( "~/.ssh")
    a_key_pair_file = os.path.join( a_key_pair_dir, a_key_pair.name ) + os.path.extsep + "pem"

    if os.path.isfile( a_key_pair_file ) :
        os.remove( a_key_pair_file )
        pass
    pass

print


print "----------- Delete EC2 security groups -----------"
for a_security_group in an_ec2_conn.get_all_security_groups() :
    if a_security_group.name != 'default' :
        print a_security_group.name
        an_ec2_conn.delete_security_group( a_security_group.name )
        pass
    pass

print


#--------------------------------------------------------------------------------------
print "---------------- Delete SQS queues ---------------"
a_sqs_conn = boto.connect_sqs( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
for a_queue in a_sqs_conn.get_all_queues() :
    print "'%s' : %d" % ( a_queue.name, a_queue.count() )
    a_queue.clear()
    a_queue.delete()
    pass

print


#--------------------------------------------------------------------------------------
print "---------------------- OK ------------------------"


#--------------------------------------------------------------------------------------
