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
