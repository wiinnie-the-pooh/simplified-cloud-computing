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
##
## See http://sourceforge.net/apps/mediawiki/balloon-foam
##
## Author : Alexey Petrov
##


#--------------------------------------------------------------------------------------
from boto.s3.connection import S3Connection
import os
a_conn=S3Connection( aws_access_key_id=os.getenv( "AWS_ACCESS_KEY_ID" ), aws_secret_access_key=os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
all_buckets = a_conn.get_all_buckets()
print  all_buckets
for a_bucket in all_buckets:
    a_bucket_prefix = a_bucket.name[:8]
    if a_bucket_prefix == "testing-":
       print "Delete ", a_bucket
       for a_key in a_bucket:
           a_key.delete()
           pass
       a_bucket.delete()
       pass
    pass


#--------------------------------------------------------------------------------------

   
